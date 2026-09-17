import numpy as np
import pygame

ball_count = int(input("Number of balls: "))
bounciness = float(input("Coefficient of restitution (0 = sticky, 1 = perfectly bouncy): "))

pygame.init()

W, H = 600, 600
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

bowl_center = np.array([W / 2, H / 2])
bowl_radius = 300
ball_radius = 10
gravity = np.array([0.0, 500.0])  


random_angle = np.random.uniform(0, 2 * np.pi, ball_count)
random_distance = (bowl_radius - ball_radius) * np.sqrt(np.random.uniform(0, 1, ball_count))  
start_x = random_distance * np.cos(random_angle)
start_y = random_distance * np.sin(random_angle)

positions = bowl_center + np.column_stack([start_x, start_y])       
velocities = np.random.uniform(-200, 200, (ball_count, 2))     

running = True

while running:
    dt = clock.tick(240) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    velocities += gravity * dt
    positions += velocities * dt

    # wall bounce
    offset_from_center = positions - bowl_center                          
    distance_from_center = np.linalg.norm(offset_from_center, axis=1)    
    touching_wall = distance_from_center > bowl_radius - ball_radius     

    if touching_wall.any():
        # [touching_wall] keeps only the rows where it is True
        hit_offsets = offset_from_center[touching_wall]                               
        hit_distances = distance_from_center[touching_wall][:, None]                  
        outward_normal = hit_offsets / hit_distances                                  

        speed_into_wall = np.sum(velocities[touching_wall] * outward_normal, axis=1, keepdims=True)   
        velocities[touching_wall] -= (1 + bounciness) * speed_into_wall * outward_normal              
        positions[touching_wall] = bowl_center + outward_normal * (bowl_radius - ball_radius)         

   
    for i in range(ball_count):
        for j in range(i + 1, ball_count):
            offset_i_to_j = positions[j] - positions[i]                  
            center_distance = np.linalg.norm(offset_i_to_j)
            if 0 < center_distance < 2 * ball_radius:
                collision_normal = offset_i_to_j / center_distance        
                approach_speed = np.dot(velocities[j] - velocities[i], collision_normal)
                if approach_speed < 0:                                    
                    impulse = (1 + bounciness) / 2 * approach_speed     
                    velocities[i] += impulse * collision_normal
                    velocities[j] -= impulse * collision_normal
                overlap = 2 * ball_radius - center_distance               
                positions[i] -= collision_normal * overlap / 2
                positions[j] += collision_normal * overlap / 2

    screen.fill("black")
    pygame.draw.circle(screen, "white", bowl_center.astype(int), bowl_radius, 2)
    for ball_position in positions:
        pygame.draw.circle(screen, "purple", ball_position.astype(int), ball_radius)

    pygame.display.flip()

pygame.quit()
