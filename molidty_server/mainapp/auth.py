
from django.forms import ValidationError
from rest_framework import views
from rest_framework.response import Response
from mainapp.models import MyManager, Worker
from mainapp.serializers import ManagerSerializer


class ManagerLoginView(views.APIView):
    """
    Login endpoint for MyManager.
    Expects JSON body: { "identifier":  "password": "..." } where "identifier" can be
    the manager's generator_name or phone. 
    Returns -->  {
            "id": manager.id,
            "user-type":'manager'    or 'worker',
            "generator_name": manager.generator_name,
            "phone": manager.phone,
            }
            
            or null if not found manager or user in same credintials
             
    """

    def post(self, request):
        identifier = request.data.get("identifier")
        requested_password = request.data.get("password")
        manager = None
        worker=None
        serialized_data={}
        if not identifier or not requested_password:
            raise ValidationError({"detail": "generator_name (or phone) and password are required."})
        
        manager = MyManager.objects.filter(generator_name=identifier,password=requested_password).first()
        if manager ==None:
                manager = MyManager.objects.filter(phone=identifier,password=requested_password).first()
        
        print(" - "*60  ,f' {identifier} no manage found ',manager)
        if manager:
                return Response(ManagerSerializer(manager))
        worker=Worker.objects.filter(name=identifier,password=requested_password).first()
        print(f'worker found {worker} with   {identifier}  {requested_password}'," + "*60  )
 
        if worker==None:
                    worker=Worker.objects.filter(phone=identifier,password=requested_password).first()
        print(f'worker found {worker} with   {identifier}  {requested_password}'," + "*60  )

        if worker:
            return Response({
              WorkerSerializer(worker)
                })
            
        return Response({"detail": "not found"},status=404)


