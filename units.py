# Copyright 2016 by Harold Fellermann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Dimensional quantities for unit aware calculations.

Quantities are values with an associated unit of a given dimension,
such as 3.3 meters, 50 seconds, 42 meters per second.
This is straight forward:

	Quantity(3.3, m=1)
	Quantity(50, s=1)
	Quantity(42, m=1, s=-1)

The first argument is the quantity's value and the keyword arguments
it's unit. Each label specifies a dimension and the number gives its
exponent. There is no restriction to the label employed, other than
being a valid python identifier -- which allows the user to calculate
in arbitrary units. Many standard units together with their metric
multiples are already defined in the module (and creating own ones is
a one-liner). With those, the handling of units becomes much simpler:

	>>> 3.3*meter
	Quantity(3.3, m=1)
	>>> 50*second
	Quantity(50, s=1)
	>>> 42*meter/second
	Quantity(42, s=-1, m=1)

Arithmetics are type safe, e.g. it is an error to add quantities of
different dimensions (with the exception that adding and subtracting 0
is allowed). Arithmetics take care of the proper handling of dimensions:

	>>> v = 45*mile/hour
	>>> print 3*hour * v
	217261.44 m
	>>> print 3*hour * v / kilometer
	217.26144

When raising quantities to fractional powers, such as second**0.5, it
can be safer to use proper fractions to avoid floating point errors:
	>>> from fractions import Fraction
	>>> print second**Fraction(1,2)
	1.0 s^1/2
"""

from decimal import Decimal, getcontext

class Quantity(object) :
	def __init__(self, value, **opts) :
		if type(value) is Quantity :
			self.value = value.value
			opts = dict(value.unit)
		elif isinstance(value, str) :
			self.value = Empirical(value)
		else :
			self.value = value
		self.unit = opts

	def __hash__(self) :
		return hash(repr(self))

	def __repr__(self) :
		unit = self.unit
		return '%s(%s, %s)' % (
			type(self).__name__,
			self.value,
			', '.join('%s=%s' % (item, unit[item]) for item in self.unit)
		)

	def __str__(self) :
		def expstr(u,e) :
			return ('%s^%s' % (u,e)) if e!=1 else u
		unit = self.unit
		unitstr = ' '.join(expstr(u,unit[u]) for u in unit)
		return "%s %s" % (self.value, unitstr)


	# comparison
	
	def __nonzero__(self) :
		return bool(self.value)

	def __eq__(self, other) :
		if not isinstance(other, Quantity) : 
			if not self.unit :
				return self.value == other
			else :
				raise NotImplementedError
		return self.value == other.value and self.unit == other.unit

	def __ne__(self, other) :
		if not isinstance(other, Quantity) : 
			if not self.unit :
				return self.value != other
			else :
				raise NotImplementedError
		return self.value != other.value or self.unit != other.unit

	def __le__(self, other) :
		if not isinstance(other, Quantity) : 
			if not self.unit :
				return self.value <= other
			else :
				raise NotImplementedError
		if self.unit != other.unit :
			raise TypeError("No ordering relation is defined for units of different dimension")
		return self.value <= other.value

	def __ge__(self, other) :
		if not isinstance(other, Quantity) : 
			if not self.unit :
				return self.value >= other
			else :
				raise NotImplementedError
		if self.unit != other.unit :
			raise TypeError("No ordering relation is defined for units of different dimension")
		return self.value >= other.value

	def __lt__(self, other) :
		if not isinstance(other, Quantity) : 
			if not self.unit :
				return self.value < other
			else :
				raise NotImplementedError
		if self.unit != other.unit :
			raise TypeError("No ordering relation is defined for units of different dimension")
		return self.value < other.value

	def __gt__(self, other) :
		if not isinstance(other, Quantity) : 
			if not self.unit :
				return self.value > other
			else :
				raise NotImplementedError
		if self.unit != other.unit :
			raise TypeError("No ordering relation is defined for units of different dimension")
		return self.value > other.value


	# conversion

	def __int__(self) :
		if self.unit :
			raise TypeError("Cannot convert dimensional quantity into int.")
		return int(self.value)

	def __long__(self) :
		if self.unit :
			raise TypeError("Cannot convert dimensional quantity into long.")
		return long(self.value)

	def __float__(self) :
		if self.unit :
			raise TypeError("Cannot convert dimensional quantity into float.")
		return float(self.value)

	def __complex__(self) :
		if self.unit :
			raise TypeError("Cannot convert dimensional quantity into complex.")
		return complex(self.value)

	# arithmetics

	def __pos__(self) :
		return Quantity(+self.value, **self.unit)

	def __neg__(self) :
		return Quantity(-self.value, **self.unit)

	def __abs__(self) :
		return Quantity(abs(self.value), **self.unit)

	def __add__(self,other) :
		if not isinstance(other, Quantity) and not other :
			return Quantity(self)
		elif not isinstance(other, Quantity) :
			if not self.unit :
				return Quantity(self.value + other)
			else :
				raise TypeError("Cannot add %s and %s." % (self, other))
		if self.unit != other.unit :
			raise TypeError("Cannot add %s and %s." % (self, other))
		else :
			return Quantity(self.value + other.value, **self.unit)

	def __radd__(self,other) :
		if not isinstance(other, Quantity) and not other :
			return Quantity(self)
		elif not isinstance(other, Quantity) and not self.unit :
			return self + other
		else :
			raise TypeError("Cannot add %s and %s." % (self, other))

	def __sub__(self,other) :
		if not isinstance(other, Quantity) and not other :
			return Quantity(self)
		if not isinstance(other, Quantity) :
			if not self.unit :
				return Quantity(self.value - other)
			else :
				raise TypeError("Cannot add %s and %s." % (self, other))
		if self.unit != other.unit :
			raise TypeError("Cannot subtract %s and %s." % (self, other))
		else :
			return Quantity(self.value - other.value, **self.unit)

	def __rsub__(self,other) :
		if not isinstance(other, Quantity) and not other :
			return Quantity(-self.value, **self.unit)
		elif not isinstance(other, Quantity) and not self.unit :
			return -self + other
		else :
			raise TypeError("Cannot subtract %s and %s." % (self, other))

	def __mul__(self, other) :
		if isinstance(other, Quantity) :
			unit = dict(self.unit)
			for u in other.unit :
				unit[u] = unit.get(u,0) + other.unit[u]
			return Quantity(self.value * other.value, **unit).simplify()
		else :
			return Quantity(self.value * other, **self.unit)

	def __rmul__(self, other) :
		return Quantity(self.value * other, **self.unit).simplify()

	def __div__(self, other) :
		if isinstance(other, Quantity) :
			unit = dict(self.unit)
			for u in other.unit :
				unit[u] = unit.get(u,0) - other.unit[u]
			return Quantity(self.value / other.value, **unit).simplify()
		else :
			return Quantity(self.value / other, **self.unit)

	def __rdiv__(self, other) :
		unit = dict((u,-self.unit[u]) for u in self.unit)
		return Quantity(other / self.value, **unit).simplify()

	def __divmod__(self, other) :
		raise RuntimeError('XXX')

	def __floordiv__(self, other) :
		if isinstance(other, Quantity) :
			unit = dict(self.unit)
			for u in other.unit :
				unit[u] = unit.get(u,0) - other.unit[u]
			return Quantity(self.value // other.value, **unit).simplify()
		else :
			return Quantity(self.value // other, **self.unit)

	def __mod__(self, other) :
		raise RuntimeError('XXX')

	def __pow__(self, other) :
		unit = dict((u,self.unit[u]*other) for u in self.unit)
		return Quantity(self.value**other, **unit)

	def simplify(self) :
		unit = self.unit
		if not any(unit.values()) : return float(self.value)
		zeros = [u for u in unit if unit[u]==0]
		for u in zeros : del self.unit[u]
		return self

	def as_latex(self, unit, format="%g") :
		try :
			string = str(format % (self/unit))
		except TypeError :
			raise ValueError("Cannot convert %s to %s" % (self, unit))
		if 'e' in string :
			mantisse,exponent = string.split('e')
			if exponent.startswith('+') :
				exponent = exponent[1:].lstrip('0')
			return r'%s \times 10^{%s}' % (mantisse,exponent)
		else :
			return string


def inject_metric_unit(namespace, name, quantity) :
	factors = {
		'tera'  : int(1e12),
		'giga'  : int(1e9),
		'mega'  : int(1e6),
		'kilo'  : int(1e3),
		'hecto' : int(1e2),
		'deca'  : int(1e1),
		''      : int(1e0),
		'deci'  : 1e-1,
		'centi' : 1e-2,
		'milli' : 1e-3,
		'micro' : 1e-6,
		'nano'  : 1e-9,
		'pico'  : 1e-12,
		'femto' : 1e-15,
	}
	for prefix in factors :
		namespace[prefix+name] = factors[prefix]*quantity


# standard units

from fractions import Fraction

# SI base units
inject_metric_unit(globals(), 'meter',   Quantity(1,   m   = Fraction(1)) )
inject_metric_unit(globals(), 'second',  Quantity(1,   s   = Fraction(1)) )
inject_metric_unit(globals(), 'gram',    Quantity(1e-3,kg  = Fraction(1)) )
inject_metric_unit(globals(), 'ampere',  Quantity(1,   A   = Fraction(1)) )
inject_metric_unit(globals(), 'kelvin',  Quantity(1,   K   = Fraction(1)) )
inject_metric_unit(globals(), 'candela', Quantity(1,   cd  = Fraction(1)) )
inject_metric_unit(globals(), 'mol',     Quantity(1,   mol = Fraction(1)) )
inject_metric_unit(globals(), 'bit',     Quantity(1,   bit = Fraction(1)) )

# Units officially accepted for use with the SI
minute  = 60*second
hour    = 60*minute
day     = 24*hour
hectare = (100*meter)**2
inject_metric_unit(globals(), 'liter', (0.1*meter)**3 )
inject_metric_unit(globals(), 'tonne', 1000*kilogram  )

# derived units
inject_metric_unit(globals(), 'hertz',   second**-1               )
inject_metric_unit(globals(), 'newton',  kilogram*meter/second**2 )
inject_metric_unit(globals(), 'pascal',  newton/meter**2          )
inject_metric_unit(globals(), 'joule',   newton*meter             )
inject_metric_unit(globals(), 'watt',    joule/second             )
inject_metric_unit(globals(), 'coulomb', ampere*second            )
inject_metric_unit(globals(), 'volt',    watt/ampere              )
inject_metric_unit(globals(), 'farad',   coulomb/volt             )
inject_metric_unit(globals(), 'ohm',     volt/ampere              )
inject_metric_unit(globals(), 'carnot',  joule/kelvin             )

# common units not officially sanctioned
angstrom = 0.1*nanometer
dyne     = 1e-5*newton
erg      = 100*nanojoule
cal      = 4.184*joule
kcal     = 1000*cal
inject_metric_unit(globals(), 'bar',      1.e5*pascal )
inject_metric_unit(globals(), 'clausius', kcal/kelvin )

# non-metric units
mile = 1.609344*kilometer
gallon = 3.78541178*liter
inch = 2.54*centimeter

# constants
Avogadro  = 6.02214179e23/mol
Boltzmann = 1.3806488e-23*joule/kelvin
Planck    = 6.62606957e-34*joule*second
