import settings
from forms import ResponseForm
from django.shortcuts import render, render_to_response
from models import Survey, Category
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required


def Index(request):
    return render(request, 'index.html')


@login_required
def SurveyDetail(request, id):
    survey = Survey.objects.get(id=id)
    category_items = Category.objects.filter(survey=survey)
    categories = [c.name for c in category_items]
    if request.method == 'POST':
        form = ResponseForm(request.POST, survey=survey, request=request)
        if form.is_valid():
            response = form.save()
            return HttpResponseRedirect("/confirm/%s" % response.interview_uuid)
    else:
        form = ResponseForm(survey=survey, request=request)
    return render_to_response('survey.html',
                              RequestContext(request,
                                             {'response_form': form,
                                              'survey': survey,
                                              'categories': categories}))


def Confirm(request, uuid):
    email = settings.support_email
    return render(request, 'confirm.html', {'uuid': uuid, "email": email})


def privacy(request):
    return render(request, 'privacy.html')


from registration.backends.simple.views import RegistrationView


class MyRegistrationView(RegistrationView):

    def get_success_url(self, request, user):
        return settings.LOGIN_REDIRECT_URL
