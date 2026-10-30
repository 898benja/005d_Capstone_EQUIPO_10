from django.contrib import admin
from services.admin import BusinessReadOnlyAdmin
from .models import MaterialExtra, PaymentOrder, ServiceMessage, ServiceDispute, ProviderWarning
for model in [MaterialExtra, PaymentOrder, ServiceMessage, ProviderWarning]:
    admin.site.register(model, BusinessReadOnlyAdmin)

from django import forms
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from rest_framework.exceptions import APIException
from .disputes import resolve
import base64


class ReviewForm(forms.Form):
    decision=forms.ChoiceField(label='Decisión',choices=[('REJECT','Rechazar reclamo'),('REFUND','Reembolsar demo y registrar alerta')])
    note=forms.CharField(label='Fundamento de la revisión',min_length=10,max_length=2000,widget=forms.Textarea)


@admin.register(ServiceDispute)
class DisputeAdmin(BusinessReadOnlyAdmin):
    list_display=['id','service_request','status','created_at','review_link']
    list_filter=['status']

    def get_urls(self):
        return [path('<int:pk>/review/',self.admin_site.admin_view(self.review_view),name='billing_dispute_review')]+super().get_urls()

    @admin.display(description='Resolución')
    def review_link(self,obj):
        return format_html('<a href="{}">Revisar reclamo</a>',reverse('admin:billing_dispute_review',args=[obj.pk]))

    def review_view(self,request,pk):
        from django.core.exceptions import PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied
        item=get_object_or_404(ServiceDispute,pk=pk)
        form=ReviewForm(request.POST or None)
        if request.method=='POST' and form.is_valid():
            try:
                resolve(item.pk,request.user,**form.cleaned_data)
                self.message_user(request,'Resolución registrada. No se ha movido dinero real.')
                return redirect('admin:billing_servicedispute_changelist')
            except APIException as error:
                form.add_error(None,str(error.detail))
        photos=[]
        for evidence in item.service_request.evidence.all():
            with evidence.photo.open('rb') as file:
                photos.append({'caption':evidence.caption,'image':base64.b64encode(file.read()).decode()})
        return render(request,'admin/billing/review.html',{
            **self.admin_site.each_context(request),'title':f'Revisión del reclamo #{item.pk}',
            'item':item,'form':form,'photos':photos,
        })
