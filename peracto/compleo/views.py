# -*- encoding: utf-8 -*-#
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from compleo.models import PeractoList, Topic, Theme, Goal, RandomName
from django.views.decorators.csrf import csrf_exempt

# When people go to www.webpage.com | POST: none
def index(request):
    random = RandomName.objects.order_by('?')[0]
    context = {
        'title': random, # the list
    }
    return render(request, 'compleo/index.html', context)

def result(request, title, message, pk):
    context = {
        'title': title, # the list
        'message': message,
        'pk': pk    
    }
    return render(request, 'compleo/results.html', context)

# When people go to www.webpage.com/listname
# POST {listname: new_or_old_listname}
def get_list(request, listname):
    peractolist = PeractoList.objects.filter(title=listname)
    if not (peractolist): 
        # Vi lager ny, uten barn og returnerer
        peractolist = PeractoList.objects.create(title=listname)
        peractolist.save()
        context = {
            'list': peractolist # the list
        }
    else:
        peractolist = peractolist[0]
        topics = Topic.objects.filter(parentList = peractolist)
        for topic in topics:
            topic.children = Theme.objects.filter(parentTopic = topic)
            for theme in topic.children:
                theme.children = Goal.objects.filter(parentTheme = theme)
        context = {
            'list': peractolist, # the list
            'topics': topics    
        }
    return render(request, 'compleo/todo.html', context)

# INTERNAL FUNCTIONS
# This could possibly be merged with the two functions below
def find_goal(key, title):
    # key can be string...
    if key != '0' and key != 0:
        # ...and this will still run smoothly
        goal = Goal.objects.filter(pk=key)
    else:
        goal = Goal.objects.filter(title=string).order_by('-pk')
    if (goal):
        # When you do a query you get a queryset as result, not the actual object
        return goal[0]
    else:
        return False

def find_topic(key, title):
    if key != '0' and key != 0:
        topic = Topic.objects.filter(pk=key)
    else:
        topic = Topic.objects.filter(title=string).order_by('-pk')
    if (topic):
        return topic[0]
    else:
        return False

def find_theme(key, title):
    if key != '0' and key != 0:
        theme = Theme.objects.filter(pk=key)
    else:
        theme = Theme.objects.filter(title=string).order_by('-pk')
    if (theme):
        return theme[0]
    else:
        return False

def delete_topic(key, title):
    topic = find_topic(key, title)
    if (topic):
        topic.delete()
        return key
    return 0

def rename_topic(key, oldTitle, newTitle):
    topic = find_topic(key, oldTitle)
    if (topic):
        topic.title=newTitle
        topic.save()
        return topic.pk
    return 0

def add_topic(name, listpk):
    plist = PeractoList.objects.filter(pk=listpk)[0]
    topic = Topic.objects.create(title=name, parentList=plist)
    topic.save()
    return topic.pk

def delete_theme(key, title):
    theme = find_theme(key, title)
    if (theme):
        theme.delete()
        return key
    return 0

def rename_theme(key, oldTitle, newTitle):
    theme = find_theme(key, oldTitle)
    if (theme):
        theme.title=newTitle
        theme.save()
        return theme.pk
    return 0

def add_theme(title, topickey, topictitle):
    parent = find_topic(topickey, topictitle)
    if (parent):
        theme = Theme.objects.create(title=title, parentTopic=parent)
        theme.save()
        return theme.pk
    return 0

def delete_goal(key, title):
    goal = find_goal(key, title)
    if (goal):
        goal.delete()
        return key
    return 0

def rename_goal(key, oldTitle, newTitle):
    goal = find_goal(key, oldTitle)
    if (goal):
        goal.title=newTitle
        goal.save()
        return goal.pk
    return 0

def add_goal(title, themekey, themetitle):
    parent = find_theme(themekey, themetitle)
    if (parent):
        goal = Goal.objects.create(title=title, parentTheme=parent)
        goal.save()
        return goal.pk
    return 0

def check_goal(key, title, uncheck):
    goal = find_goal(key, title)
    if (goal):
        if (uncheck):
            goal.checked = False
        else:
            goal.checked = True
        goal.save()

@csrf_exempt
def rename(request):
    # type|this.pk|this.oldTitle|this.newTitle
    if request.method == 'POST':
        operations = request.POST['operations'].split(';')
        for operation in operations:
            print "rename: " + operation
            objecttype, key, oldTitle, newTitle = operation.split('|') 
            if objecttype.lower() == 'topic':
                pk = rename_topic(key, oldTitle, newTitle)
                return result(request, "Topic successfully renamed " + newTitle, "I love you", pk)
            elif objecttype.lower() == 'theme':
                pk = rename_theme(key, oldTitle, newTitle)
                return result(request, "Theme successfully renamed " + newTitle, "I love you", pk)
            elif objecttype.lower() == 'goal':
                pk = rename_goal(key, oldTitle, newTitle)
                return result(request, "Goal successfully renamed " + newTitle, "I love you", pk)
    else:
        return result(request, "You need to provide more stuff", "", "")

@csrf_exempt
def check(request):
    if request.method == 'POST':
        operations = request.POST['operations'].split(';')
        for operation in operations:
            print "check: " + operation
            check, key, title = operation.split('|') 
            if check == '0':
                check_goal(key, title, True)
                print "goal was unchecked"
                return result(request, "Goal successfully unchecked " + title, "I love you", key)
            else:
                check_goal(key, title, False)
                print "goal was checked"
                return result(request, "Goal successfully checked " + title, "I love you", key)
    else:
        return result(request, "You need to provide more stuff", "", "")

@csrf_exempt
def add(request):
    # Type|parent.pk|parent.title|this.title
    if request.method == 'POST':
        operations = request.POST['operations'].split(';')
        for operation in operations:
            print "add: " + operation
            objecttype, parentkey, parenttitle, title = operation.split('|') 
            if objecttype.lower() == 'topic':
                pk = add_topic(title, parentkey)
                return result(request, "Topic successfully added", "I love you", pk)
            elif objecttype.lower() == 'theme':
                pk = add_theme(title, parentkey, parenttitle)
                return result(request, "Theme successfully added", "I love you", pk)
            elif objecttype.lower() == 'goal':
                pk = add_goal(title, parentkey, parenttitle)
                return result(request, "Goal successfully added", "I love you", pk)
    else:
        return result(request, "You need to provide more stuff", "", "")

@csrf_exempt
def delete(request):
    # Type|this.pk|this.title
    if request.method == 'POST':
        operations = request.POST['operations'].split(';')
        for operation in operations:
            print "delete: " + operation
            objecttype, key, title = operation.split('|') 
            if objecttype.lower() == 'topic':
                pk = delete_topic(key, title)
                return result(request, "Topic successfully removed", "I love you", pk)
            elif objecttype.lower() == 'theme':
                pk = delete_theme(key, title)
                return result(request, "Theme successfully removed", "I love you", pk)
            elif objecttype.lower() == 'goal':
                pk = delete_goal(key, title)
                return result(request, "Goal successfully removed", "I love you", pk)
    else:
        return result(request, "You need to provide more stuff", "", "")