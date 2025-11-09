"""Cliente asyncio de ejemplo que abre múltiples conexiones concurrentes al servidor TCP.

Usar para probar concurrencia y asincronía de I/O.
"""
import asyncio


async def talk(host: str, port: int, message: str):
    reader, writer = await asyncio.open_connection(host, port)
    # recibir bienvenida
    data = await reader.readuntil(b"\n")
    print('Servidor:', data.decode().strip())
    writer.write((message + '\n').encode('utf-8'))
    await writer.drain()
    # leer respuestas hasta timeout corto
    try:
        while True:
            line = await asyncio.wait_for(reader.readline(), timeout=0.5)
            if not line:
                break
            print('Respuesta:', line.decode().strip())
    except asyncio.TimeoutError:
        pass
    writer.write(b'QUIT\n')
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def main():
    host = '127.0.0.1'
    port = 5001
    # lanzar varios clientes concurrentes
    tasks = []
    for i in range(3):
        # pedir lista y luego intentar reservar el slot 1 (demo)
        msg = 'LIST'
        tasks.append(asyncio.create_task(talk(host, port, msg)))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
