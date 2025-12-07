from bleak import BleakClient


class BLEController:
    def __init__(self, device_address: str = "34:B7:DA:5E:81:15"):
        self.device_address = device_address

    async def send(self, value: str) -> bool:
        try:
            async with BleakClient(self.device_address) as client:
                services = client.services
                for service in services:
                    for char in service.characteristics:
                        if (
                            "write" in char.properties
                            or "write-without-response" in char.properties
                        ):
                            message_bytes = value.encode()
                            await client.write_gatt_char(char.uuid, message_bytes)
                            print(f"BLE sent: {value}")
                            return True

                print("No write characteristic found")
                return False
        except Exception as e:
            print(f"BLE error: {e}")
            return False
