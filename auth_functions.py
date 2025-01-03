from supabase_config import supabase

def registrar_usuario(email, password):
    try:
        respuesta = supabase.auth.sign_up({"email": email, "password": password})
        print("Usuario registrado correctamente:", respuesta)
        return respuesta
    except Exception as e:
        print("Error al registrar usuario:", e)
        return None

def iniciar_sesion(email, password):
    try:
        respuesta = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print("Inicio de sesión exitoso:", respuesta)
        return respuesta
    except Exception as e:
        print("Error al iniciar sesión:", e)
        return None

def obtener_usuario_actual():
    try:
        usuario = supabase.auth.get_user()
        print("Usuario actual:", usuario)
        return usuario
    except Exception as e:
        print("Error al obtener usuario actual:", e)
        return None
