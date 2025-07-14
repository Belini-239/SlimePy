# SlimePy
A simple language for competitions from AIA
#### Code example:

```
{
  v: number = $ball_velocity.y
  h: number = $ball_position.y
  g: number = -$gravity
  t: number = (v + sqrt(v * v + 2 * g * h)) / g
  print(t)
  fall_pos: vec3 = $ball_velocity * t + $ball_position

  x: number = fall_pos.x
  z: number = fall_pos.z

  if (z > 3.2) { z = 3.2 - (z - 3.2) * 0.6 }
  if (z < -3.2) { z = -3.2 + (-3.2 - z) * 0.6 }

  if (x > 6.5) { x = 6.5 - (x - 6.5) * 0.6 }
  if (x < -6.5) { x = -6.5 + (-6.5 - x) * 0.6 }

  fall_pos = vec3(x + 0.3 * sign($self_position.x), 0.01, z)

  draw_disc(fall_pos, 0.3, 0.1, COLOR.RED)


  if ((x <= 0 xor $self_position.x <= 0) or abs(x) <= 0.2) {
    fall_pos = vec3(sign($self_position.x) * 3.0, 0, 0)
  }
  $slime_move_to = fall_pos
  draw_disc(fall_pos, 1, 0.2, COLOR.GREEN)

  $slime_jump = false
  if (distance($self_position, $ball_position) <= 1.5) {
    $slime_jump = true
    $slime_move_to = $ball_position
  }
}
```

## Usage
1. Download full project
2. Run main.py with the path to the source code file and the path to the output file
```py C:\path\to\main.py C:\path\to\source.sp C:\path\to\output.txt```
(You can make a simple bash script if you want)

## Basic Syntax
### Types
SlimePy has strong typing. There are 3 types of variables:
- vec3
- number
- bool

#### Vec3
To make vector use
```vec3(x, y, z)```

You can get a component of a vector using
```vector.x vector.y vector.z```
But you cannot assign anithing to it (You cannot write this: ```vector.x = 10```)

Operators: ```+, -, *(scale), *(dot production), ^(cross production)```

#### Number
Basic number, but there is no !=

#### Bool
Basic bool

Operators: ```and, or, xor, xnor, nor, nand```

#### Color
You cannot make variables of type ```color```, but you can use ```COLOR.<color>``` in functions
##### List of colors
```
COLOR.BLACK
COLOR.BLUE
COLOR.BROWN
COLOR.HOTPINK
COLOR.LIGHTBLUE
COLOR.LIGHTGREY
COLOR.MEDIUMGREY
COLOR.ORANGE
COLOR.PINK
COLOR.PURPLE
COLOR.RED
COLOR.WHITE
COLOR.YELLOW
```

### Variables
#### Variables Declaration
```variable_name: type = value```
#### Variable Assignment
```variable_name = value```

#### Built-in variables
There are several registered variables that are used as alternatives to GetBool(), GetFloat() and GetVector3() from the visual language. You can use them in your calclations, but **YOU CANNOT ASSIGN A VALUE TO THEM**
##### List of built-in variables (they start with '$'):
```
$self_can_jump: bool
$opponent_can_jump: bool
$ball_is_self_side: bool

$delta_time: number
$fixed_delta_time: number
$gravity: number
$pi: number
$simulation_duration: number
$team_score: number
$opponent_score: number
$touches_remain: number

$self_position: vec3
$self_velocity: vec3
$ball_position: vec3
$ball_velocity: vec3
$opponent_position: vec3
$opponent_velocity: vec3
```

#### Output variables
There are also the same variables, but they are used to output information to the Controller. You can assign a value to such variables, **BUT YOU CANNOT USE THEM IN CALCULATIONS**.

##### List of output variables (they also start with '$')
```
$slime_move_to: vec3
$slime_jump: bool
```

### if
Syntax:
```
if (condition)
{
  true_block
}
```
else has not been done yet

### Functions
Right now, there are only built-in functions.

#### List of functions
```
clamp(value: number, min: number, max: number) -> number

abs(x: number) -> number
round(x: number) -> number
floor(x: number) -> number
ceil(x: number) -> number
sin(x: number) -> number
cos(x: number) -> number
tan(x: number) -> number
asin(x: number) -> number
acos(x: number) -> number
atan(x: number) -> number
sqrt(x: number) -> number
sign(x: number) -> number
log(x: number) -> number   # natural logarithm
log10(x: number) -> number
pow_e(x: number) -> number  # e raised to the power x
pow_10(x: number) -> number # 10 raised to the power x

random(min: number, max: number) -> number

distance(start: vec3, end: vec3) -> number
len(vector: vec3) -> number
norm(vector: vec3) -> vec3

draw_line(start: vec3, end: vec3, thickness: number, c: color) -> none
draw_disc(pos: vec3, radius: number, thickness: number, c: color) -> none
print(value: any)
```
