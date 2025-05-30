import pygame
import random
import threading
import cv2
import mediapipe as mp

pygame.init()

# Game window
width, height = 500, 500
game_screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Hand Snake Game")

# Snake setup
snake_x, snake_y = width / 2, height / 2
change_x, change_y = 0, 0
snake_body = [(snake_x, snake_y)]
food_x, food_y = random.randrange(0, width, 10), random.randrange(0, height, 10)
score = 0
speed = 6
paused = False
font = pygame.font.SysFont(None, 35)

clock = pygame.time.Clock()

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
gesture_command = ""

# Gesture detection function
def detect_gesture():
    global gesture_command
    ret, frame = cap.read()
    if not ret:
        return
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger_tip = hand_landmarks.landmark[8]
            middle_finger_tip = hand_landmarks.landmark[12]

            x_diff = middle_finger_tip.x - index_finger_tip.x
            y_diff = middle_finger_tip.y - index_finger_tip.y

            if abs(x_diff) > abs(y_diff):
                if x_diff > 0.1:
                    gesture_command = "left"
                elif x_diff < -0.1:
                    gesture_command = "right"
            else:
                if y_diff > 0.1:
                    gesture_command = "up"
                elif y_diff < -0.1:
                    gesture_command = "down"
    cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to close
        pygame.quit()
        cap.release()
        cv2.destroyAllWindows()
        quit()

# Game logic
def display_snake_and_food():
    global snake_x, snake_y, food_x, food_y, score, speed

    snake_x = (snake_x + change_x) % width
    snake_y = (snake_y + change_y) % height

    if (snake_x, snake_y) in snake_body[1:]:
        print("Game Over. Score:", score)
        pygame.quit()
        quit()

    snake_body.append((snake_x, snake_y))

    if food_x == snake_x and food_y == snake_y:
        score += 1
        food_x, food_y = random.randrange(0, width, 10), random.randrange(0, height, 10)
        if score % 5 == 0:
            speed += 1
    else:
        del snake_body[0]

    game_screen.fill((0, 0, 0))
    pygame.draw.rect(game_screen, (0, 255, 0), [food_x, food_y, 10, 10])
    for (x, y) in snake_body:
        pygame.draw.rect(game_screen, (255, 255, 255), [x, y, 10, 10])

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    game_screen.blit(score_text, (10, 10))

    if paused:
        pause_text = font.render("Paused - Press P", True, (255, 0, 0))
        game_screen.blit(pause_text, (width // 6, height // 2))

    pygame.display.update()

# Main game loop
while True:
    events = pygame.event.get()
    key_pressed = False

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            cv2.destroyAllWindows()
            quit()
        if event.type == pygame.KEYDOWN:
            key_pressed = True
            if event.key == pygame.K_p:
                paused = not paused
            if not paused:
                if event.key == pygame.K_LEFT:
                    change_x = -10
                    change_y = 0
                elif event.key == pygame.K_RIGHT:
                    change_x = 10
                    change_y = 0
                elif event.key == pygame.K_UP:
                    change_x = 0
                    change_y = -10
                elif event.key == pygame.K_DOWN:
                    change_x = 0
                    change_y = 10

    if not paused:
        detect_gesture()

        if not key_pressed:
            move_cmd = gesture_command

            if move_cmd:
                print("Move:", move_cmd)

            if "up" in move_cmd:
                change_x = 0
                change_y = -10
            elif "down" in move_cmd:
                change_x = 0
                change_y = 10
            elif "left" in move_cmd:
                change_x = -10
                change_y = 0
            elif "right" in move_cmd:
                change_x = 10
                change_y = 0

            gesture_command = ""

        display_snake_and_food()
    clock.tick(speed)
