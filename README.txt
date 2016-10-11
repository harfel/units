Dimensional quantities for unit aware calculations

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
