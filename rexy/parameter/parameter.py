# coding:utf-8

import json
from .base import Array, NonFiles, Comparables

try:
    unicode is unicode

except NameError:
    unicode = str


class Group(object):
    def __init__(self, mapping):
        self._mapping = mapping

    def __contains__(self, key):
        return self._mapping.__contains__(key)

    def __len__(self):
        return self._mapping.__len__()

    def __iter__(self):
        return self._mapping.__iter__()

    def __getitem__(self, key):
        try:
            obj = self._mapping[key]

        except:
            return Items((e for e in []))

        else:
            if isinstance(obj, dict):
                return self.__cls__(obj)

            elif isinstance(obj, (list, tuple)):
                return self.__cls__((e for e in obj))

            else:
                return self.__cls__((e for e in (obj,)))

    def __getattr__(self, name):
        return self.__getitem__(name)


class Items(Array):
    @staticmethod
    def prefilter(v):
        return v

    def values(self):
        return self.to(Strings)

    def files(self):
        return self.to(Files)


class Files(Array):
    @staticmethod
    def prefilter(v):
        if not self.is_fieldstorage(v):
            raise TypeError('Must be a file')

        return v

    def values(self):
        return self.apply(lambda fs: fs.value).to(Strings)

    @staticmethod
    def _mimetype(fs, typ, subtypes=None):
        mtype = fs.type.split('/')
        if len(mtype) == 2:
            t, st = mtype
            if t == typ:
                if subtypes is None:
                    return fs

                else:
                    if st in subtypes:
                        return fs

        raise TypeError('Unacceptable mimetype')

    def mimetype(self, typ, subtypes=None):
        return self.apply(self._mimetype, typ, subtypes)


class Strings(NonFiles):
    @staticmethod
    def prefilter(v):
        if not isinstance(v, (bytes, unicode)):
            raise TypeError()

        return v

    @staticmethod
    def _encode(v, encoding):
        return v.encode(encoding) if isinstance(v, unicode) else v

    @staticmethod
    def _decode(v, encoding):
        return v.decode(encoding) if isinstance(v, bytes) else v

    def encode(self, encoding='utf-8'):
        return self.where(self._encode, encoding)

    def decode(self, encoding='utf-8'):
        return self.where(self._decode, encoding)

    @staticmethod
    def _len_le(v, border):
        if border < len(v):
            raise ValueError('Too long (max length: {})'.format(border))

        return v

    @staticmethod
    def _len_ge(v, border):
        if len(v) < border:
            raise ValueError('Too short (min length: {})'.format(border))

        return v

    def len_le(self, border):
        return self.apply(self._len_le, border)

    def len_ge(self, border):
        return self.apply(self._len_ge, border)

    def of_int(self):
        return self.to(Ints)

    def of_float(self):
        return self.to(Floats)

    def of_date(self, fmt='%Y/%m/%d'):
        return self.to(Dates, fmt)

    def of_datetime(self, fmt='%Y/%m/%d %H:%M:%S'):
        return self.to(DateTimes, fmt)

    def of_csv(self, separator=',', strip=True):
        return self.to(Csv)

    def of_json(self):
        return self.to(Json)


class Csv(NonFiles):
    @staticmethod
    def prefilter(v, separator, strip):
        g = (e.strip() if strip else e for e in v.split(separator))
        return Strings(g)


class Json(NonFiles):
    @staticmethod
    def prefilter(v):
        return Group(json.loads(v))


class Ints(Comparables):
    @staticmethod
    def prefilter(v):
        return int(v)


class Floats(Comparables):
    @staticmethod
    def prefilter(v):
        return float(v)


class Dates(Comparables):
    @staticmethod
    def prefilter(v, fmt):
        return datetime.strptime(v, fmt).date()


class DateTimes(Comparables):
    @staticmethod
    def prefilter(v, fmt):
        return datetime.strptime(v, fmt)