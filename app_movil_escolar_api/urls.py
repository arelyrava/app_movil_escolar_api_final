from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app_movil_escolar_api.views import users, alumnos, maestros, auth, evento

urlpatterns = [
    # Create Admin
    path('admin/', users.AdminView.as_view()),
    
    # Admin Data
    path('lista-admins/', users.AdminAll.as_view()),
    
    # Create Alumno
    path('alumnos/', alumnos.AlumnosView.as_view()),
    
    # Create Maestro
    path('maestros/', maestros.MaestrosView.as_view()),
    
    # Maestro Data
    path('lista-maestros/', maestros.MaestrosAll.as_view()),
    
    # Alumno Data
    path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
    
    # Total Usuarios
    path('total-usuarios/', users.TotalUsers.as_view()),
    
      
    # Evento por ID
    path('eventos/<int:id>/', evento.EventosView.as_view()),
    
    # Evento Data
    path('eventos/', evento.EventosView.as_view()),
    
    # Lista de eventos
    path('lista-eventos/', evento.EventosAll.as_view()),
    
    # Login
    path('login/', auth.CustomAuthToken.as_view()),
    
    # Logout
    path('logout/', auth.Logout.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)