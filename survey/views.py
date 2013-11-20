import settings
from forms import ResponseForm
from django.shortcuts import render
from models import Survey, Category
from django.http import HttpResponseRedirect


def Index(request):
    return render(request, 'index.html')


def SurveyDetail(request, id):
    survey = Survey.objects.get(id=id)
    category_items = Category.objects.filter(survey=survey)
    categories = [c.name for c in category_items]
    print 'categories for this survey:'
    print categories
    if request.method == 'POST':
        form = ResponseForm(request.POST, survey=survey)
        if form.is_valid():
            response = form.save()
            return HttpResponseRedirect("/confirm/%s" % response.interview_uuid)
    else:
        form = ResponseForm(survey=survey)
    return render(request, 'survey.html',
                  {'response_form': form, 'survey': survey,
                   'categories': categories})


def Confirm(request, uuid):
    email = settings.support_email
    return render(request, 'confirm.html', {'uuid': uuid, "email": email})


def privacy(request):
    return render(request, 'privacy.html')
