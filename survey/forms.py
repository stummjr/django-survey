import uuid
from django import forms
from django.forms import models
from django.utils.safestring import mark_safe
from survey.models import Question, Response, Answer


# blatantly stolen from
# http://stackoverflow.com/questions/5935546/
#  align-radio-buttons-horizontally-in-django-forms?rq=1
class HorizontalRadioRenderer(forms.RadioSelect.renderer):

    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class ResponseForm(models.ModelForm):

    class Meta:
        model = Response
        fields = ('comments',)

    def __init__(self, *args, **kwargs):
        # expects a survey object to be passed in initially
        data = kwargs.get('data')
        self.user = kwargs.pop('request').user
        survey = kwargs.pop('survey')
        self.survey = survey
        super(ResponseForm, self).__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex
        for q in survey.questions():
            self.fields["question_%d" % q.pk] = self.__build_field(q, data)

    def __build_field(self, q, data):
        if q.question_type == Question.TEXT:
            field = forms.CharField(label=q.text, widget=forms.Textarea)
        elif q.question_type == Question.RADIO:
            field = forms.ChoiceField(label=q.text,
                                      widget=forms.RadioSelect(
                                      renderer=HorizontalRadioRenderer),
                                      choices=q.get_choices())
        elif q.question_type == Question.SELECT:
            choices = tuple([('', '-------------')]) + q.get_choices()
            field = forms.ChoiceField(label=q.text,
                                      widget=forms.Select,
                                      choices=choices)
        elif q.question_type == Question.SELECT_MULTIPLE:
            field = forms.MultipleChoiceField(
                label=q.text,
                widget=forms.CheckboxSelectMultiple,
                choices=q.get_choices())
        elif q.question_type == Question.INTEGER:
            field = forms.IntegerField(label=q.text)

        field.required = q.required
        # if the field is required, give it a corresponding css class.
        if q.required:
            field.widget.attrs["class"] = "required"

        # add the category as a css class, and add it as a data attribute
        # as well (this is used in the template to allow sorting the
        # questions by category)
        if q.category:
            self.__add_category_to_field(field, q)

        # initialize the form field with values from a POST request, if
        # any.
        if data:
            field.initial = data.get('question_%d' % q.pk)

        return field

    def __add_category_to_field(self, field, q):
        classes = field.widget.attrs.get("class")
        if classes:
            field.widget.attrs["class"] = (classes +
                                           (" cat_%s" % q.category.name))
        else:
            field.widget.attrs["class"] = (" cat_%s" % q.category.name)
        field.widget.attrs["category"] = q.category.name
        return field

    def save(self, commit=True):
        response = super(ResponseForm, self).save(commit=False)
        response.survey = self.survey
        response.interviewee = self.user
        response.interview_uuid = self.uuid
        response.save()

        # create an answer object for each question and associate it with this
        # response.
        for field_name, field_value in self.cleaned_data.iteritems():
            if field_name.startswith("question_"):
                # warning: this way of extracting the id is very fragile and
                # entirely dependent on the way the question_id is encoded in
                # the field name in the __init__ method of this form class.
                q_id = int(field_name.split("_")[1])
                q = Question.objects.get(pk=q_id)
                a = Answer(question=q)
                a.body = field_value
                a.response = response
                a.save()
        return response
