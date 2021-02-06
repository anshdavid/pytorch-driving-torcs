import numpy as np
import matplotlib.pyplot as plt

class Agent(object):
    def __init__(self, dim_action):
        self.dim_action = dim_action

    def act(self, ob, reward, done, vision_on):

        if vision_on is False:
            focus, speedX, speedY, speedZ, opponents, rpm, track, wheelSpinVel = ob
        else:
            focus, speedX, speedY, speedZ, opponents, rpm, track, wheelSpinVel, vision = ob

            # print(vision.shape)
            # img = np.ndarray((64,64,3))
            # for i in range(3):
            #     img[:, :, i] = 255 - vision[:, i].reshape((64, 64))

            # plt.imshow(img, origin='lower')
            # plt.draw()
            # plt.pause(0.001)

        # random action
        return np.tanh(np.random.randn(self.dim_action))    #type:ignore
