import operator
from celery import Celery
import celeryconfig

app = Celery('tasks')
app.config_from_object(celeryconfig)

@app.task
def div(x,y):
    res = x/y
    print("div({0},{1})={2}".format(x,y,res))
    return res

@app.task
def add_list(lst):
    res = reduce(operator.__add__,lst)
    print("add_list({0})={1}".format(lst,res))
    return res

@app.task
def add(a, b):
    res = a + b
    print("add(%d,%d)=%d" % (a,b,res))
    return res


@app.task
def mul(a, b):
    res = a * b
    print("mul(%d,%d)=%d" %(a,b,res))
    return res

