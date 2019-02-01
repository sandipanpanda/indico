# This file is part of Indico.
# Copyright (C) 2002 - 2019 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired

from indico.util.i18n import _
from indico.web.flask.util import url_for
from indico.web.forms.base import IndicoForm
from indico.web.forms.widgets import SelectizeWidget


class ContributionField(QuerySelectField):
    """A selectize-based field to select a contribution from an event
    that hasn't been linked to a reservation.
    """

    widget = SelectizeWidget(allow_by_id=True, search_field='title', label_field='full_title', preload=True,
                             search_method='POST', inline_js=True)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('allow_blank', True)
        kwargs.setdefault('render_kw', {}).setdefault('placeholder', _('Enter contribution title or #id'))
        kwargs['get_label'] = lambda a: '#{}: {}'.format(a.friendly_id, a.title)
        self.ajax_endpoint = kwargs.pop('ajax_endpoint')
        super(ContributionField, self).__init__(*args, **kwargs)

    @classmethod
    def _serialize_contrib(cls, contrib):
        return {'id': contrib.id, 'friendly_id': contrib.friendly_id, 'title': contrib.title,
                'full_title': '#{}: {}'.format(contrib.friendly_id, contrib.title)}

    def _value(self):
        return self._serialize_contrib(self.data) if self.data else None

    def pre_validate(self, form):
        super(ContributionField, self).pre_validate(form)
        if self.data is not None and self.data.id in self.excluded_abstract_ids:
            raise ValueError(_('This contribution cannot be selected.'))

    @property
    def event(self):
        # This cannot be accessed in __init__ since `get_form` is set
        # afterwards (when the field gets bound to its form) so we
        # need to access it through a property instead.
        return self.get_form().event

    @property
    def search_url(self):
        return url_for(self.ajax_endpoint, self.event)


class SessionBlockField(QuerySelectField):
    pass  # TODO


class BookingListForm(IndicoForm):
    contribution = ContributionField(_("Contribution"), [DataRequired()], description=_("Enter the contribution name."),
                                     ajax_endpoint='contributions.other_contributions')

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        super(BookingListForm, self).__init__(*args, **kwargs)