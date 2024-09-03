import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt5.QtCore import Qt, QTimer

# Define constants
WIDTH, HEIGHT = 800, 800 
ROWS, COLS = 20, 20 
CELL_SIZE = WIDTH // COLS
PADDING = 16  

# Colors
WHITE = QColor("#FFFFFF")
BLACK = QColor("#000000")
RED = QColor("#FF0000") # Color for current cell
BLUE = QColor("#0000FF")  #Color for backtracking 

# Initialize maze grid
# 2D array to keep track of visited cells and walls
maze = [[{'visited': False, 'walls': [True, True, True, True]} for _ in range(COLS)] for _ in range(ROWS)]

# Function to remove walls between two cells
def remove_walls(current, next):
    x1, y1 = current
    x2, y2 = next
    if x1 == x2:  
        if y1 > y2:  # Up
            maze[x1][y1]['walls'][3] = False
            maze[x2][y2]['walls'][2] = False
        else:  # Down
            maze[x1][y1]['walls'][2] = False
            maze[x2][y2]['walls'][3] = False
    elif y1 == y2:  
        if x1 > x2:  # Left
            maze[x1][y1]['walls'][1] = False
            maze[x2][y2]['walls'][0] = False
        else:  # Right
            maze[x1][y1]['walls'][0] = False
            maze[x2][y2]['walls'][1] = False


class MazeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.speed = 50
        self.instant_finish = False 
        self.generation_running = False 
        self.initUI() 

    def initUI(self):
        self.setGeometry(100, 100, WIDTH + 2 * PADDING, HEIGHT + 2 * PADDING)
        self.setWindowTitle('Maze Generator')
        self.show()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_maze)
        self.start_maze_generation()  
    
   
    # Depth-first search algorithm 
    def depth_first_search(self):
        current = self.stack[-1]
        x, y = current
        neighbors = []
        # Find all unvisited neighbors
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + direction[0], y + direction[1]
            if 0 <= nx < ROWS and 0 <= ny < COLS and not maze[nx][ny]['visited']:
                neighbors.append((nx, ny))
        if neighbors:
            # Choose a random unvisited neighbor
            next_cell = random.choice(neighbors)
            remove_walls(current, next_cell)
            maze[next_cell[0]][next_cell[1]]['visited'] = True
            self.stack.append(next_cell)
        else:
            # Backtrack if no unvisited neighbors
            self.stack.pop()


    def start_maze_generation(self):
        if self.generation_running:
            self.timer.stop()
        else:
            if not self.stack:
                self.stack = [(0, 0)]
                maze[0][0]['visited'] = True # Mark the starting cell as visited
            self.timer.start(self.speed)
        self.generation_running = not self.generation_running

    # Reset the maze
    def reset_maze(self):
        global maze
        maze = [[{'visited': False, 'walls': [True, True, True, True]} for _ in range(COLS)] for _ in range(ROWS)]
        self.stack = []
        self.instant_finish = False
        self.generation_running = False
        self.timer.stop()
        self.update()

    # Update the maze 
    def update_maze(self):
        # If the stack is empty, the maze is complete
        # Stop the timer and save the maze as an image
        if not self.stack:
            self.timer.stop()
            self.save_maze("generated_maze.png") 
            return
        
        self.depth_first_search()

        self.update()

        if self.instant_finish:
            self.timer.setInterval(1)
        else:
            self.timer.setInterval(self.speed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(BLACK, 2, Qt.SolidLine))
        painter.fillRect(self.rect(), WHITE)

        for x in range(ROWS):
            for y in range(COLS):
                cell = maze[x][y]
                cell_x = x * CELL_SIZE + PADDING
                cell_y = y * CELL_SIZE + PADDING
                if cell['visited']:
                    painter.fillRect(cell_x, cell_y, CELL_SIZE, CELL_SIZE, WHITE)
                if cell['walls'][0]:  # Right wall
                    painter.drawLine(cell_x + CELL_SIZE, cell_y, cell_x + CELL_SIZE, cell_y + CELL_SIZE)
                if cell['walls'][1]:  # Left wall
                    painter.drawLine(cell_x, cell_y, cell_x, cell_y + CELL_SIZE)
                if cell['walls'][2]:  # Bottom wall
                    painter.drawLine(cell_x, cell_y + CELL_SIZE, cell_x + CELL_SIZE, cell_y + CELL_SIZE)
                if cell['walls'][3]:  # Top wall
                    painter.drawLine(cell_x, cell_y, cell_x + CELL_SIZE, cell_y)

        # Highlight the current cell
        if self.stack:
            current = self.stack[-1]
            # Determine if we are backtracking by checking if the stack size is decreasing
            color = BLUE if len(self.stack) > 1 and not any(0 <= current[0] + dx < ROWS and 0 <= current[1] + dy < COLS and not maze[current[0] + dx][current[1] + dy]['visited'] for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]) else RED
            painter.fillRect(current[0] * CELL_SIZE + PADDING, current[1] * CELL_SIZE + PADDING, CELL_SIZE, CELL_SIZE, color)

    # Handle key presses
    # Up arrow key decreases the speed
    # Down arrow key increases the speed
    # F key finishes the maze instantly
    # S key stops and starts the maze generation
    # R key resets the maze 
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.speed = max(10, self.speed - 10)
        elif event.key() == Qt.Key_Down:
            self.speed += 10
        elif event.key() == Qt.Key_F:
            self.instant_finish = True
        elif event.key() == Qt.Key_S:
            self.start_maze_generation()
        elif event.key() == Qt.Key_R:
            self.reset_maze()
    
    # Save the maze as an image
    def save_maze(self, filename):
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        pixmap.save(filename)

def main():
    app = QApplication(sys.argv)
    ex = MazeWidget()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()