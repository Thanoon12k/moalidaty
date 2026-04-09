
from django.forms import ValidationError
from rest_framework import views
from rest_framework.response import Response
from mainapp.models import Account, Worker
from mainapp.serializers import AccountSerializer, WorkerSerializer


class AccountLoginView(views.APIView):
 
    def post(self, request):
        identifier = request.data.get("identifier")
        requested_password = request.data.get("password")
        account = None
        if not identifier or not requested_password:
            raise ValidationError({"detail": "generator_name (or phone) and password are required."})
        
        account = Account.objects.filter(generator_name=identifier,password=requested_password).first()
        if account ==None:
                account = Account.objects.filter(phone=identifier,password=requested_password).first()
        
        if account:
                return Response(AccountSerializer(account).data)
                    
        return Response({"detail": "not found"},status=404)


class WokerLoginView(views.APIView):
 
    def post(self, request):
        identifier = request.data.get("identifier")
        requested_password = request.data.get("password")
        account=None
        worker =None 
        
        if not identifier or not requested_password:
            raise ValidationError( "fields -> identifier (generator name or phone) and password are required.")
        
        account = Account.objects.filter(generator_name=identifier).first()
        if account:
            gen_id=Account.objects.filter(id=account.id).first().id
            worker=Worker.objects.filter(generator=gen_id,password=requested_password).first()


        if worker ==None:
            worker=Worker.objects.filter(phone=identifier,password=requested_password).first()

        if worker:
                return Response(WorkerSerializer(worker).data)
             
        return Response({"detail": "not found"},status=404)


