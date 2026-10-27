"""
Modelo para el cálculo de la nómina y sueldos (Ajustado a la LOTTT Venezuela).
"""

from models.database import conectar

def calcular_nomina_mensual():
    """
    Calcula cuánto se le debe pagar a cada empleado según la LOTTT de Venezuela.
    
    Fórmulas aplicadas:
    - Sueldo diario = Sueldo Base / 30 días.
    - Valor hora normal = Sueldo diario / 8 horas.
    - Horas extras se pagan con un recargo del 50% (valor_hora * 1.5).
    
    Retorna una lista de diccionarios con el reporte de cada empleado.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        # 1. Buscamos todos los empleados que estén activos
        cursor.execute("SELECT id, cedula, nombre, apellido, cargo, sueldo_base FROM empleados WHERE estado = 'Activo'")
        empleados = cursor.fetchall()
        
        reporte = []
        for emp in empleados:
            # 2. Sumamos todas las horas trabajadas por el empleado en todos sus marcajes
            cursor.execute("SELECT SUM(horas_trabajadas) FROM marcajes WHERE empleado_id = ?", (emp["id"],))
            resultado = cursor.fetchone()
            horas_totales = resultado[0] if resultado[0] else 0.0
            
            # 3. Separación de Horas Normales y Extras:
            # Según la LOTTT, la jornada diaria es de 8 horas. Para este cálculo estimado,
            # asumimos que por cada bloque de 8 horas trabajadas, se completa un día.
            dias_trabajados = int(horas_totales // 8)
            horas_normales = dias_trabajados * 8
            # Las horas que sobren de esos bloques de 8 se consideran extras
            horas_extras = horas_totales - horas_normales

            # 4. Fórmulas LOTTT Venezuela para el cálculo del pago
            if emp["sueldo_base"] > 0:
                # Sueldo Base mensual se divide entre 30 días
                sueldo_diario = emp["sueldo_base"] / 30.0
                # El sueldo diario se divide entre las 8 horas de la jornada
                valor_hora_normal = sueldo_diario / 8.0
                # Las horas extras tienen un recargo del 50% (Art. 118 LOTTT)
                valor_hora_extra = valor_hora_normal * 1.5 
            else:
                # Prevención de división por cero si el empleado no tiene sueldo asignado
                sueldo_diario = 0.0
                valor_hora_normal = 0.0
                valor_hora_extra = 0.0
                
            # 5. Cálculo del pago total
            pago_normal = horas_normales * valor_hora_normal
            pago_extra = horas_extras * valor_hora_extra
            pago_total = pago_normal + pago_extra
            
            # 6. Armamos el diccionario con los resultados para la Vista
            reporte.append({
                "cedula": emp["cedula"],
                "nombre": f"{emp['nombre']} {emp['apellido']}",
                "cargo": emp["cargo"],
                "sueldo_base": emp["sueldo_base"],
                "horas_trabajadas": horas_totales,
                "horas_extras": horas_extras,
                "pago_total": pago_total
            })
            
        return reporte
    finally:
        conn.close()