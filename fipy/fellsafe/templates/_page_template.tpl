{% args req %}
<!DOCTYPE html>
<html>
Request path: '{{req.path}}'<br>
<table border="1">
{% for i in range(5) %}
<tr><td> {{i}} </td><td> {{"%2d" % i ** 2}} </td></tr>
{% endfor %}
</table>
</html

Syntax:

Evaluating Python expression, converting it to a string and outputting to rendered content:

    {{<expr>}}

Where expr is an arbitrary Python expression - from a bare variable name, to function calls, yield from, await expressions.

Supported statements:

    {% if %}, {% elif %}, {% else %}, {% endif %} - the usual "if" statement
    {% for %}, {% endfor %} - the usual "for" statement
    {% while %}, {% endwhile %} - the usual "while" statement
    {% args var1, var2, ... %} - specify arguments to a template
    {% set var = expr %} - assignment statement
    {% include "name.tpl" %} - statically include another template
    {% include {{name}} %} - dynamically include template whose name is stored in variable name.

Naming Conventions

The current conventions (may be adjusted in the future):

    The recommended extension for templates is .tpl, e.g. example.tpl.
    When template is compiled, dot (.) in its name is replaced with underscore (_) and .py appended, e.g. example_tpl.py. It thus can be imported with import example_tpl.
    The name passed to {% include %} statement should be full name of a template with extension, e.g. {% include "example.tpl" %}.
    For dynamic form of the include, a variable should similarly contain a full name of the template, e.g. {% set name = "example.tpl" %} / {% include {{name}} %}.
