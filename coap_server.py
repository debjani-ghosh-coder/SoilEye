import asyncio
import aiocoap.resource as resource
import aiocoap

class Soil(resource.Resource):
    async def render_post(self, request):
        print("Received:", request.payload.decode())
        return aiocoap.Message(code=aiocoap.CHANGED)

root = resource.Site()
root.add_resource(['soil'], Soil())

async def main():
    await aiocoap.Context.create_server_context(
        root,
        bind=("10.81.251.55", 5683)
    )
    print("CoAP server running...")
    await asyncio.get_running_loop().create_future()

asyncio.run(main())