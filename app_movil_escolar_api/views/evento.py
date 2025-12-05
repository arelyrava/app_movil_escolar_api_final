from django.db.models import *
from django.db import transaction
from app_movil_escolar_api.serializers import EventoSerializer
from app_movil_escolar_api.models import Evento, Administradores, Maestros, Alumnos
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
import json
from django.shortcuts import get_object_or_404
from django.db.models import Q

# Vista para LISTAR todos los eventos 
class EventosAll(generics.CreateAPIView):
    # Aquí se valida la autenticación del usuario
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Admins ven todos los eventos
        if user.is_superuser or Administradores.objects.filter(user=user).exists():
            eventos = Evento.objects.all().order_by('id')
        
        # Maestros ven eventos para Profesores o Público general
        elif Maestros.objects.filter(user=user).exists():
            eventos = Evento.objects.filter(
                Q(publico_objetivo__icontains='Profesores') | 
                Q(publico_objetivo__icontains='Público en general')
            ).order_by('id')
        
        # Alumnos ven eventos para Estudiantes o Público general
        elif Alumnos.objects.filter(user=user).exists():
            eventos = Evento.objects.filter(
                Q(publico_objetivo__icontains='Estudiantes') | 
                Q(publico_objetivo__icontains='Público en general')
            ).order_by('id')
        
        # Si no tiene rol válido, no ve nada
        else:
            eventos = Evento.objects.none()
        
        lista = EventoSerializer(eventos, many=True).data
        return Response(lista, 200)


 
class EventosView(generics.CreateAPIView):
    # Permisos por método 
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [] # POST no requiere autenticación

    # Función auxiliar para verificar si es admin
    def es_admin(self, user):
        return user.is_superuser or Administradores.objects.filter(user=user).exists()

    # Función auxiliar para verificar si puede ver el evento
    def puede_ver_evento(self, user, evento):
        # Admins pueden ver todo
        if self.es_admin(user):
            return True
        
        # Maestros pueden ver eventos para Profesores o Público general
        if Maestros.objects.filter(user=user).exists():
            return (evento.publico_objetivo and 
                   ('Profesores' in evento.publico_objetivo or 
                    'Público en general' in evento.publico_objetivo))
        
        # Alumnos pueden ver eventos para Estudiantes o Público general
        if Alumnos.objects.filter(user=user).exists():
            return (evento.publico_objetivo and 
                   ('Estudiantes' in evento.publico_objetivo or 
                    'Público en general' in evento.publico_objetivo))
        
        return False

    # Obtener evento por ID 
    def get(self, request, *args, **kwargs):
        
        evento_id = kwargs.get('id') or request.GET.get("id")
        
        if not evento_id:
            return Response({"message": "Se requiere el parámetro 'id'"}, 400)
        
        evento = get_object_or_404(Evento, id=evento_id)
        
        # Validar que el usuario pueda ver este evento específico
        if not self.puede_ver_evento(request.user, evento):
            return Response({"message": "No tienes permiso para ver este evento"}, 403)
        
        evento_data = EventoSerializer(evento, many=False).data
        return Response(evento_data, 200)

    # Registrar nuevo evento 
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Verificar que sea admin
        if not self.es_admin(request.user):
            return Response(
                {"message": "Acción denegada. Solo los administradores pueden registrar eventos."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EventoSerializer(data=request.data)
        if serializer.is_valid():
            evento = serializer.save()
            return Response({"Evento creado con ID= ": evento.id }, 201)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar datos del evento 
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Verificar que sea admin
        if not self.es_admin(request.user):
            return Response(
                {"message": "Acción denegada. No tienes permisos para editar eventos."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        
        evento_id = kwargs.get('id') or request.data.get("id")
        
        if not evento_id:
            return Response({"message": "Se requiere el campo 'id'"}, 400)
        
        
        evento = get_object_or_404(Evento, id=evento_id)
        
        # Actualizar los campos
        evento.nombre = request.data.get("nombre", evento.nombre)
        evento.tipo = request.data.get("tipo", evento.tipo)
        evento.fecha = request.data.get("fecha", evento.fecha)
        evento.hora_inicio = request.data.get("hora_inicio", evento.hora_inicio)
        evento.hora_fin = request.data.get("hora_fin", evento.hora_fin)
        evento.lugar = request.data.get("lugar", evento.lugar)
        evento.publico_objetivo = request.data.get("publico_objetivo", evento.publico_objetivo)
        evento.programa_educativo = request.data.get("programa_educativo", evento.programa_educativo)
        evento.responsable = request.data.get("responsable", evento.responsable)
        evento.descripcion = request.data.get("descripcion", evento.descripcion)
        evento.cupo = request.data.get("cupo", evento.cupo)
        
        evento.save()
        
        # Respuesta de éxito
        return Response({
            "message": "Evento actualizado correctamente",
            "evento": EventoSerializer(evento).data
        }, 200)

    # Eliminar evento 
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        # Verificar que sea admin
        if not self.es_admin(request.user):
            return Response(
                {"message": "Acción denegada. No tienes permisos para eliminar eventos."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        
        evento_id = kwargs.get('id') or request.GET.get("id")
        
        if not evento_id:
            return Response({"message": "Se requiere el parámetro 'id'"}, 400)
        
        
        evento = get_object_or_404(Evento, id=evento_id)
        
        try:
            evento.delete()
            return Response({"details": "Evento eliminado"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al intentar eliminar el evento"}, 400)