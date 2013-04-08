# Copyright 2012 VPAC
#
# This file is part of django-tldap.
#
# django-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-tldap  If not, see <http://www.gnu.org/licenses/>.

"""
This module implements a transaction manager that can be used to define
transaction handling in a request or view function. It is used by transaction
control middleware and decorators.

The transaction manager can be in managed or in auto state. Auto state means
the system is using a commit-on-save strategy (actually it's more like
commit-on-change). As soon as the .save() or .delete() (or related) methods are
called, a commit is made.

Managed transactions don't do those commits, but will need some kind of manual
or implicit commits or rollbacks.
"""
import sys

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

import tldap.transaction
import placard.ldap_bonds as bonds


class TransactionManagementError(Exception):
    """
    This exception is thrown when something bad happens with transaction
    management.
    """
    pass


def enter_transaction_management():
    """
    Enters transaction management for a running thread. It must be balanced
    with the appropriate leave_transaction_management call, since the actual
    state is managed as a stack.

    The state and dirty flag are carried over from the surrounding block or
    from the settings, if there is no surrounding block (dirty is always false
    when no current block is running).
    """
    master = bonds.master
    tldap.transaction.enter_transaction_management(using=master.slave_id)

    for slave in bonds.slaves.values():
        tldap.transaction.enter_transaction_management(using=slave.slave_id)


def leave_transaction_management():
    """
    Leaves transaction management for a running thread. A dirty flag is carried
    over to the surrounding block, as a commit will commit all changes, even
    those from outside. (Commits are on connection level.)
    """
    master = bonds.master
    tldap.transaction.leave_transaction_management(using=master.slave_id)

    for slave in bonds.slaves.values():
        tldap.transaction.leave_transaction_management(using=slave.slave_id)


def is_dirty():
    """
    Returns True if the current transaction requires a commit for changes to
    happen.
    """
    master = bonds.master
    if tldap.transaction.is_dirty(using=master.slave_id):
        return True

    for slave in bonds.slaves.values():
        if tldap.transaction.is_dirty(using=slave.slave_id):
            return True

    return False


def is_managed():
    """
    Checks whether the transaction manager is in manual or in auto state.
    """
    master = bonds.master
    if tldap.transaction.is_managed(using=master.slave_id):
        return True

    for slave in bonds.slaves.values():
        if tldap.transaction.is_managed(using=slave.slave_id):
            return True

    return False


def commit():
    """
    Does the commit itself and resets the dirty flag.
    """
    master = bonds.master
    tldap.transaction.commit(using=master.slave_id)

    for slave in bonds.slaves.values():
        tldap.transaction.commit(using=slave.slave_id)


def rollback():
    """
    This function does the rollback itself and resets the dirty flag.
    """
    master = bonds.master
    tldap.transaction.rollback(using=master.slave_id)

    for slave in bonds.slaves.values():
        tldap.transaction.rollback(using=slave.slave_id)

##############
# DECORATORS #
##############


class Transaction(object):
    """
    Acts as either a decorator, or a context manager.  If it's a decorator it
    takes a function and returns a wrapped function.  If it's a contextmanager
    it's used with the ``with`` statement.  In either event entering/exiting
    are called before and after, respectively, the function/block is executed.

    autocommit, commit_on_success, and commit_manually contain the
    implementations of entering and exiting.
    """
    def __init__(self, entering, exiting):
        self.entering = entering
        self.exiting = exiting

    def __enter__(self):
        self.entering()

    def __exit__(self, exc_type, exc_value, traceback):
        self.exiting(exc_value)

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            # Once we drop support for Python 2.4 this block should become:
            # with self:
            #     func(*args, **kwargs)
            self.__enter__()
            try:
                res = func(*args, **kwargs)
            except:
                self.__exit__(*sys.exc_info())
                raise
            else:
                self.__exit__(None, None, None)
                return res
        return inner


def _transaction_func(entering, exiting):
    """
    Takes 3 things, an entering function (what to do to start this block of
    transaction management), an exiting function (what to do to end it, on both
    success and failure, and using which can be: None, indiciating using is
    DEFAULT_LDAP_ALIAS, a callable, indicating that using is DEFAULT_LDAP_ALIAS
    and to return the function already wrapped.

    Returns either a Transaction objects, which is both a decorator and a
    context manager, or a wrapped function, if using is a callable.
    """
    return Transaction(entering, exiting)


def commit_on_success():
    """
    This decorator activates commit on response. This way, if the view function
    runs successfully, a commit is made; if the viewfunc produces an exception,
    a rollback is made. This is one of the most common ways to do transaction
    control in Web apps.
    """
    def entering():
        enter_transaction_management()

    def exiting(exc_value):
        try:
            if exc_value is not None:
                if is_dirty():
                    rollback()
            else:
                if is_dirty():
                    try:
                        commit()
                    except:
                        rollback()
                        raise
        finally:
            leave_transaction_management()

    return _transaction_func(entering, exiting)


def commit_manually():
    """
    Decorator that activates manual transaction control. It just disables
    automatic transaction control and doesn't do any commit/rollback of its
    own -- it's up to the user to call the commit and rollback functions
    themselves.
    """
    def entering():
        enter_transaction_management()

    def exiting(exc_value):
        leave_transaction_management()

    return _transaction_func(entering, exiting)
