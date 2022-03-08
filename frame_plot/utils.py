def overlay(background, foreground):
    # normalize alpha channels from 0-255 to 0-1
    alpha_background = background[:, :, 3] / 255.0
    alpha_foreground = foreground[:, :, 3] / 255.0

    # set adjusted colors
    for color in range(0, 3):
        background[:, :, color] = alpha_foreground * foreground[:, :, color] + \
            alpha_background * background[:, :, color] * (1 - alpha_foreground)

    # set adjusted alpha and denormalize back to 0-255
    background[:, :, 3] = (1 - (1 - alpha_foreground)
                           * (1 - alpha_background)) * 255

    return background
