---
category: cheatsheet
layout: post
modified: 2012-11-27
title: Python Cheat Sheet
---

# Sorting a list by string length

{% highlight python %}
mylist.sort(cmp=lambda x,y: len(x)-len(y))
{% endhighlight %}

# Getting # of CPUs

{% highlight python %}
os.sysconf('SC_NPROCESSORS_ONLN')
{% endhighlight %}

# Dict string substitution

[https://stackoverflow.com/q/56011/1198943](https://stackoverflow.com/q/56011/1198943)

{% highlight python linenos=table %}
LIGHT_MESSAGES = {
    'English': "There are %(number_of_lights)s lights.",
    'Pirate':  "Arr! There be %(number_of_lights)s lights."
}
def lights_message(language, number_of_lights):
    """Return a language-appropriate string reporting the light count."""
    return LIGHT_MESSAGES[language] % locals()
{% endhighlight %}

# Misc

{% highlight python %}
urls = [line.rstrip('\n\r') for line in f.readlines()]
{% endhighlight %}

{% highlight python %}
self.COLS = curses.tigetnum('cols')
{% endhighlight %}

{% highlight python %}
self.LINES = curses.tigetnum('lines')
{% endhighlight %}

{% highlight python %}
struct.unpack('hh',fcntl.ioctl(0,termios.TIOCGWINSZ,'1234'))
{% endhighlight %}

{% highlight python %}
return True if self.result[0] == 0 else False #python >= 2.5
{% endhighlight %}

{% highlight python %}
return (self.result[0] == 0 and [True] or [False])[0] #python < 2.5
{% endhighlight %}

{% highlight python %}
[t for t in [1,2,3,4] if t == 1]
{% endhighlight %}

{% highlight python %}
signal.signal(signal.SIGINT, lambda signal, frame: sys.exit(0)) # Properly handle Control+C
{% endhighlight %}
