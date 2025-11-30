from django.core.mail import send_mail
from django.conf import settings
import threading

def enviar_correo_segundo_plano(asunto, mensaje, destinatarios):
    """
    Envía correos usando hilos (threading) para que el usuario no tenga
    que esperar a que el servidor de correo responda para ver la página siguiente.
    """
    def _enviar():
        try:
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error enviando correo: {e}")
    hilo = threading.Thread(target=_enviar)
    hilo.start()

# --- FUNCIONES ESPECÍFICAS ---

def notificar_nuevo_usuario(usuario, password_generada):
    """Envía credenciales al crear un nuevo usuario."""
    asunto = "Bienvenido a ReConectaTec - Tus Credenciales"
    mensaje = f"""
    Hola {usuario.nombre},

    Bienvenido al equipo de ReConectaTec.
    Tu cuenta ha sido creada con el rol de: {usuario.rol}.

    Tus credenciales de acceso son:
    Usuario (Email): {usuario.email}
    Contraseña Temporal: {password_generada}

    IMPORTANTE: Por seguridad, ingresa a 'Mi Cuenta' y cambia esta contraseña inmediatamente.
    
    Saludos,
    Equipo ReConectaTec
    """
    enviar_correo_segundo_plano(asunto, mensaje, [usuario.email])

def notificar_ticket_soporte(ticket, usuario):
    """Confirma al usuario que su ticket fue creado."""
    asunto = f"Ticket #{ticket.id_soporte} Recibido - ReConectaTec"
    mensaje = f"""
    Hola {usuario.nombre},

    Hemos recibido tu solicitud de soporte.
    
    ID Ticket: #{ticket.id_soporte}
    Institución: {ticket.id_asignacion}
    Problema: {ticket.descripcion}

    Un técnico revisará tu caso pronto.

    Saludos,
    Soporte IT
    """
    enviar_correo_segundo_plano(asunto, mensaje, [usuario.email])

def notificar_actualizacion_perfil(usuario):
    """Avisa al usuario que sus datos fueron modificados."""
    asunto = "Seguridad: Tus datos de cuenta han sido actualizados"
    mensaje = f"""
    Hola {usuario.nombre},

    Te informamos que los datos de tu perfil en ReConectaTec han sido modificados recientemente.
    
    Si fuiste tú, puedes ignorar este mensaje.
    Si NO fuiste tú, por favor contacta al administrador inmediatamente.

    Saludos,
    Equipo de Seguridad
    """
    enviar_correo_segundo_plano(asunto, mensaje, [usuario.email])

def notificar_resolucion_soporte(ticket):
    """
    Avisa al contacto de la institución que el ticket tiene novedades.
    Ruta del email: Ticket -> Asignacion -> Institucion -> Contacto Email
    """
    try:
        destinatario = ticket.id_asignacion.rut_institucion_receptora.contacto_email
        nombre_institucion = ticket.id_asignacion.rut_institucion_receptora.nombre
    except AttributeError:
        print(">>> ERROR: No se pudo encontrar el email de la institución para notificar.")
        return

    if not destinatario:
        print(">>> AVISO: La institución no tiene email de contacto registrado.")
        return
    estado_texto = "Actualizado"
    if ticket.resolucion:
        estado_texto = "Resuelto / Respondido"

    asunto = f"Actualización Ticket #{ticket.id_soporte} - {estado_texto}"
    mensaje = f"""
    Estimados {nombre_institucion},

    El ticket de soporte #{ticket.id_soporte} ha sido actualizado por nuestro equipo técnico.

    Equipo Afectado: {ticket.id_asignacion}
    Tipo de Soporte: {ticket.tipo}
    
    --- NOVEDADES / RESOLUCIÓN ---
    {ticket.resolucion if ticket.resolucion else "El técnico ha actualizado los detalles del caso."}
    -------------------------------

    Técnico a cargo: {ticket.id_tecnico.nombre if ticket.id_tecnico else "Por asignar"}

    Saludos,
    Soporte ReConectaTec
    """
    enviar_correo_segundo_plano(asunto, mensaje, [destinatario])