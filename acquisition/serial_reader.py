import serial

def iniciar_serial(porta="COM3", baudrate=9600):
    ser = serial.Serial(porta, baudrate, timeout=1)
    return ser


def ler_serial(ser):
    try:
        linha = ser.readline().decode("utf-8", errors="ignore").strip()

        if linha:
            print("DEBUG:", linha)
            return linha  # 🔥 AQUI ESTÁ A CORREÇÃO

        return None

    except:
        return None