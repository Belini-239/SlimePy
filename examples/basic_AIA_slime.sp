{
    forward: vec3 = vec3(-sign($self_position.x), 0, 0)
    move_to: vec3 = $ball_position - forward * 0.3
    move_to = vec3(move_to.x, 0, move_to.z)
    draw_disc(move_to, 1.0, 0.1, COLOR.RED)
    $slime_move_to = move_to
    $slime_jump = distance($self_position, $ball_position) <= 1.5
}