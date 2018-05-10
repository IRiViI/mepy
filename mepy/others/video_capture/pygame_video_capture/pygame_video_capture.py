# from io import StringIO
# import base64
# from io import BytesIO
# import pygame
# import pygame.camera
# from pygame.locals import *
# from PIL import Image
# import codecs

class PygameVideoCapture(object):
    def __init__(self):
        pass
        # DEVICE = '/dev/video0'
        # SIZE = (640, 480)
        # FILENAME = 'capture.png'

        # pygame.init()
        # pygame.camera.init()
        # self.display = pygame.display.set_mode(SIZE, 0)
        # self.camera = pygame.camera.Camera(DEVICE, SIZE)
        # self.camera.start()
        # self.screen = pygame.surface.Surface(SIZE, 0, self.display)
    
    def __del__(self):
        pass
        # self.camera.stop()
        # pygame.quit()
    
    def get_frame(self):
        pass

        # def load(file):
        #     with open(file) as file:
        #         return file.read()

        # output = BytesIO()

        # self.screen = self.camera.get_image(self.screen)
        # self.display.blit(self.screen, (0,0))
        # data = self.camera.get_raw()
        # # pygame.display.update()
        # image = Image.frombytes("RGB",(120,90),data)
        # # Or
        # # webcamImage = cam.get_image()
        # # pil_string_image = pygame.image.tostring(img,"RGBA",False)
        # # image = Image.frombytes("RGBA",(1280,720),pil_string_image)
        
        # # content = image.save(output)
        # # print(content)
        # # return load('img_fjords.jpg')
        # # return data
        # with codecs.open('img_fjords.jpg', mode='rb') as f:
        #     img = f.read()
        #     print(img)
        #     # img = img..decode("utf-16")
        #     # img = str(img)
        #     # 
        #     # img = base64.b64encode(f.read())
        # # buffer = StringIO()
        # # image.save(buffer, format="JPEG")
        # return img
        # # base64.b64encode(buffer.getvalue())
        # # data.encode('utf-8')

    def show(self, screen):
        pass
        # pygame.display.flip()

    def stop(self):
        pass
        # self.__del__()