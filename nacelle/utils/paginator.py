"""
Paginator support shamelessly stolen from Django

Code: https://github.com/django/django/blob/master/django/core/paginator.py
Docs: https://docs.djangoproject.com/en/1.4/topics/pagination/
License: https://github.com/django/django/blob/master/LICENSE
"""
from math import ceil


class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass


class EmptyPage(InvalidPage):
    pass


class Paginator(object):

    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page = int(per_page)
        self.orphans = int(orphans)
        self.allow_empty_first_page = allow_empty_first_page
        self._num_pages = self._count = None

    def validate_number(self, number):
        "Validates the given 1-based page number."
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return number

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(self.object_list[bottom:top], number, self)

    def _get_count(self):
        "Returns the total number of objects, across all pages."
        if self._count is None:
            try:
                self._count = self.object_list.count()
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)

    def _get_num_pages(self):
        "Returns the total number of pages."
        if self._num_pages is None:
            if self.count == 0 and not self.allow_empty_first_page:
                self._num_pages = 0
            else:
                hits = max(1, self.count - self.orphans)
                self._num_pages = int(ceil(hits / float(self.per_page)))
        return self._num_pages
    num_pages = property(_get_num_pages)

    def _get_page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a template for loop.
        """
        return range(1, self.num_pages + 1)
    page_range = property(_get_page_range)

QuerySetPaginator = Paginator  # For backwards-compatibility.


class Page(object):
    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.paginator.num_pages)

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        # The object_list is converted to a list so that if it was a QuerySet
        # it won't be a database hit per __getitem__.
        return list(self.object_list)[index]

    # The following four methods are only necessary for Python <2.6
    # compatibility (this class could just extend 2.6's collections.Sequence).

    def __iter__(self):
        i = 0
        try:
            while True:
                v = self[i]
                yield v
                i += 1
        except IndexError:
            return

    def __contains__(self, value):
        for v in self:
            if v == value:
                return True
        return False

    def index(self, value):
        for i, v in enumerate(self):
            if v == value:
                return i
        raise ValueError

    def count(self, value):
        return sum([1 for v in self if v == value])

    # End of compatibility methods.

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.number + 1

    def previous_page_number(self):
        return self.number - 1

    def start_index(self):
        """
        Returns the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        # Special case, return zero if no items.
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        # Special case for the last page because there can be orphans.
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page


def paginate(objects, page_num, items_per_page=20, padding_pages=3):

    """
        Automatically works out pagination variables based on the passed arguments.  If an invalid page is called the last page will be returned instead. If a non-int page number is used the view will return the first page.

        Returns a dict which can be added to the context in the view with 'context = dict(context.items() + paginate(blah, blah).items())'

        Args:
            objects: A list or queryset (any slicable object) with the objects to be paginated
            page_num: int num of current page to display
            items_per_page: int number of items to display per page (default: 20)

        Returns:
            context: dict containing values which can be added to the contaxt and used for pagination

        Example markup:

            <ul>
                <li {% if not firstPage %}class="active"{% endif %}>
                    <a href="?page={{ firstPage }}">First</a>
                </li>
                <li {% if not prevPage %}class="active"{% endif %}>
                    <a href="?page={{ prevPage }}">Previous</a>
                </li>
                {% for p in pages %}
                    <li {% if p == current_page %}class="active"{% else %}{% if p == "..." %}class="disabled"{% endif %}{% endif %}>
                        <a href="?page={{p}}">{{p}}</a>
                    </li>
                {% endfor %}
                <li {% if not nextPage %}class="active"{% endif %}>
                    <a href="?page={{ nextPage }}">Next</a>
                </li>
                <li {% if not lastPage %}class="active"{% endif %}>
                    <a href="?page={{ lastPage }}">Last</a>
                </li>
            </ul>

    """

    context = {}
    paginate = Paginator(objects, items_per_page)

    try:
        page = paginate.page(page_num)
        context['current_page'] = int(page_num)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginate.page(1)
        context['current_page'] = 1
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginate.page(paginate.num_pages)
        context['current_page'] = paginate.num_pages

    context['objects'] = page.object_list
    context['totalPages'] = paginate.num_pages

    startPage = max(context['current_page'] - padding_pages - 1, 0)
    endPage = context['current_page'] + padding_pages
    context['pages'] = paginate.page_range[startPage:endPage]

    if page.has_next():
        context['nextPage'] = page.next_page_number()
        context['lastPage'] = paginate.num_pages
    else:
        context['nextPage'] = False
        context['lastPage'] = False

    if page.has_previous():
        context['prevPage'] = page.previous_page_number()
        context['firstPage'] = 1
    else:
        context['prevPage'] = False
        context['firstPage'] = False

    if not 1 in context['pages']:
        context['pages'].insert(0, '...')
    if not paginate.num_pages in context['pages']:
        context['pages'].append('...')

    return context