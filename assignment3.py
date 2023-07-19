import math
from math import sqrt

import glfw
from OpenGL.GL import *


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Node(Point):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hasHandle1 = False
        self.hasHandle2 = False
        self.handle1 = Point(0, 0)
        self.handle2 = Point(0, 0)


'''
Contains all the necessary functions to render the splines.
'''
SCREEN_WIDTH = int(input("Screen Width: "))
SCREEN_HEIGHT = int(input("Screen Height: "))


class Scene:
    def __init__(self):
        self.curve = []
        self.is_dragging = False
        self.is_ctrl_point_dragging = False
        self.handle_position = -1
        self.ctrl_position = -1
        self.ctrl_points = []
        self.is_Point = True
        self.is_CtrlPoint = True

    # implements decasteljau's formula for cubic bezier curve
    def DeCasteljau_Curve(self, points):
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)

        for i in range(len(points) - 1):
            p0 = points[i]
            p3 = points[i+1]
            p1 = points[i].handle2
            p2 = points[i+1].handle1
            glColor3f(0.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)

            for j in range(200):
                t = j / 200.0
                x = ((1-t)**3 * p0.x) + (3*(1-t)**2 * t * p1.x) + \
                    (3*(1-t) * t**2 * p2.x) + (t**3 * p3.x)
                y = ((1-t)**3 * p0.y) + (3*(1-t)**2 * t * p1.y) + \
                    (3*(1-t) * t**2 * p2.y) + (t**3 * p3.y)
                glVertex2f(x, y)
            glEnd()

    # Creates square points where the mouse clicks.
    def add_points(self, points):
        glPointSize(20)
        glColor3f(1.0, 0.647, 0)

        glBegin(GL_POINTS)
        for node in points:
            glVertex2f(node.x, node.y)
        glEnd()

    # Smoother control points
    def show_ctrl_points(self, points):
        glEnable(GL_BLEND)
        glEnable(GL_POINT_SMOOTH)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glPointSize(10)
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_POINTS)
        i = 0
        while i < len(points):
            node = points[i]
            if node.hasHandle1:
                glVertex2f(node.handle1.x, node.handle1.y)
            if node.hasHandle2:
                glVertex2f(node.handle2.x, node.handle2.y)
            i += 1
        glEnd()
        glDisable(GL_POINT_SMOOTH)

    # Create dotted handle
    def render_dot_line(self, points):
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(2, 0xAAAA)

        # Set color to light green
        glColor4f(0.5, 0.9, 0.565, 1)
        glBegin(GL_LINES)
        i = 0
        while i < len(points):
            node = points[i]
            if node.hasHandle1:
                glVertex2f(node.handle1.x, node.handle1.y)
                glVertex2f(node.x, node.y)

            if node.hasHandle2:
                glVertex2f(node.handle2.x, node.handle2.y)
                glVertex2f(node.x, node.y)

            i += 1

        glEnd()
        glDisable(GL_LINE_STIPPLE)

    '''

    HELPER FUNCTIONS

    '''

    # Gets the closest endpoint using euclidean distance.
    def closest_endpoint(self, currNode, firstNode, SecondNode):
        dist_1 = math.dist((currNode.x, currNode.y),
                           (firstNode.x, firstNode.y))
        dist_2 = math.dist((currNode.x, currNode.y),
                           (SecondNode.x, SecondNode.y))
        return firstNode if dist_1 < dist_2 else SecondNode

    # Distance between two nodes.
    def distance(self, FirstNode, SecondNode):
        dx, dy = SecondNode.x - FirstNode.x, SecondNode.y - FirstNode.y
        return sqrt(dx ** 2 + dy ** 2)

    # Determines position of new nodes using displacement of nodes.
    def getNewPoints(self, currPointHandleX, currPointx, currPointHandleY, currPointy):
        dx = (currPointHandleX - currPointx)
        dy = (currPointHandleY - currPointy)
        newX = currPointx - dx
        newY = currPointy - dy
        return newX, newY

    # Correctly posiiton intermediate handles + move curve accordingly.
    def nextPoint(self, currPoint, nextPoint):
        if (self.is_CtrlPoint):
            if self.ctrl_position > 0:
                if (self.ctrl_position == 1):
                    newX, newY = self.getNewPoints(
                        currPoint.handle1.x, currPoint.x, currPoint.handle1.y, currPoint.y)
                if currPoint.handle1.x - currPoint.x == 0:
                    newX = currPoint.x
                    newY = currPoint.y - nextPoint
                elif self.ctrl_position == 2:
                    newX, newY = self.getNewPoints(
                        currPoint.handle2.x, currPoint.x, currPoint.handle2.y, currPoint.y)
            else:
                newX, newY = self.getNewPoints(
                    currPoint.handle1.x, currPoint.x, currPoint.handle1.y, currPoint.y)

        return (newX, newY)

    # If we are dragging, reposition accordingly.
    def isDragging(self, window):
        x, y = glfw.get_cursor_pos(window)
        node = self.curve[self.handle_position]
        dx, dy = x - node.x, SCREEN_HEIGHT - y - node.y
        node.x += dx
        node.y += dy
        if (node.hasHandle2 and self.is_Point):
            node.handle2.x += dx
            node.handle2.y += dy
        if (node.hasHandle1 and self.is_Point):
            node.handle1.x += dx
            node.handle1.y += dy
        self.curve[self.handle_position] = node

    # If we are dragging control point, reposition accordingly.
    def isCtrlPointDragging(self, window):
        x, y = glfw.get_cursor_pos(window)
        node = self.curve[self.handle_position]
        if (self.is_Point):
            if self.ctrl_position == 1:
                dx = x - node.handle1.x
                dy = SCREEN_HEIGHT - y - node.handle1.y
                node.handle1.x += dx
                node.handle1.y += dy
                self.curve[self.handle_position].handle1.x, self.curve[self.handle_position].handle1.y = node.handle1.x, node.handle1.y
                if self.curve[self.handle_position].hasHandle2:
                    self.curve[self.handle_position].handle2.x, self.curve[self.handle_position].handle2.y = self.nextPoint(
                        self.curve[self.handle_position], self.distance(self.curve[self.handle_position], self.curve[self.handle_position].handle1))

            else:
                dx = x - node.handle2.x
                dy = SCREEN_HEIGHT - y - node.handle2.y
                node.handle2.x += dx
                node.handle2.y += dy
                self.curve[self.handle_position].handle2.x, self.curve[self.handle_position].handle2.y = node.handle2.x, node.handle2.y
                self.curve[self.handle_position].handle1.x, self.curve[self.handle_position].handle1.y = self.nextPoint(
                    self.curve[self.handle_position], self.distance(self.curve[self.handle_position], self.curve[self.handle_position].handle2))

    # Handles left click interaction, resetting attributes.
    def handle_node_interaction(self, current_node, node_exists, is_ctrl_point):
        for node in self.curve:
            if node.hasHandle1:
                if self.distance(node.handle1, current_node) <= 30:
                    is_ctrl_point = True
                    node_exists = True
                    current_node = node
                    self.ctrl_position = 1

            if node.hasHandle2:
                if self.distance(node.handle2, current_node) <= 30:
                    is_ctrl_point = True
                    node_exists = True
                    current_node = node
                    self.ctrl_position = 2

            if self.distance(node, current_node) <= 30:
                node_exists = True
                current_node = node

        return current_node, node_exists, is_ctrl_point

    # Handles where to add the new node, given the criteria described.
    def handleNodeAddition(self, window, nodeExists, current_node, is_ctrl_point):
        mouseX, mouseY = glfw.get_cursor_pos(window)
        mouseY = SCREEN_HEIGHT - mouseY
        if not nodeExists:
            new_node = Point(mouseX, mouseY + 50)
            current_node.handle1 = new_node
            current_node.hasHandle1 = True
            self.ctrl_points.append(new_node)
            if len(self.curve) < 1:
                self.curve.insert(0, current_node)
            else:
                endpoint = self.closest_endpoint(
                    current_node, self.curve[0], self.curve[len(self.curve) - 1])
                if endpoint is self.curve[0]:
                    self.curve.insert(0, current_node)
                else:
                    self.curve.append(current_node)

                middle_node = endpoint
                adj_point = self.nextPoint(middle_node, self.distance(
                    middle_node, middle_node.handle1))

                middle_node.hasHandle2 = True
                middle_node.handle2.x = adj_point[0]
                middle_node.handle2.y = adj_point[1]
        else:
            if nodeExists:
                if (is_ctrl_point):
                    self.is_ctrl_point_dragging = True
                    self.handle_position = self.curve.index(current_node)
                else:
                    self.handle_position = self.curve.index(current_node)
                    self.is_dragging = True


'''
Handles the setup and interactions.
'''
class RenderWindow:
    def __init__(self):
        if not glfw.init():
            return
        self.window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, "Spline Tool", None, None)

        # set the context and callbacks
        if not self.window:
            glfw.terminate()
            return
        glfw.make_context_current(self.window)
        glClearColor(1, 1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
        glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        glfw.set_cursor_pos_callback(self.window, self.onMouseMove)
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)

        self.scene = Scene()

    def onMouseMove(self, window, x, y):
        if (self.scene.is_Point):
            if self.scene.is_ctrl_point_dragging:
                self.scene.isCtrlPointDragging(window)
            if self.scene.is_dragging == True:
                self.scene.isDragging(window)

    def onKeyboard(self, window, key, scancode, action, mods):
        if key == glfw.KEY_E:
            self.scene.curve.clear()

    def onMouseButton(self, window, button, action, mods):
        node_exists = False
        is_ctrl_point = False

        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                mouseX, mouseY = glfw.get_cursor_pos(window)
                mouseY = SCREEN_HEIGHT - mouseY
                current_node = Node(mouseX, mouseY)

                current_node, node_exists, is_ctrl_point = self.scene.handle_node_interaction(
                    current_node, node_exists, is_ctrl_point)

                self.scene.handleNodeAddition(window, node_exists,
                                              current_node, is_ctrl_point)
            elif action == glfw.RELEASE:
                self.scene.is_dragging = False
                self.scene.is_ctrl_point_dragging = False
                self.scene.ctrl_position = -1

    def run(self):
        # loop
        while not glfw.window_should_close(self.window):
            glfw.window_hint(glfw.SAMPLES, 4)
            glEnable(GL_MULTISAMPLE)
            glClear(GL_COLOR_BUFFER_BIT)

            self.scene.DeCasteljau_Curve(self.scene.curve)
            self.scene.add_points(self.scene.curve)
            self.scene.show_ctrl_points(self.scene.curve)
            self.scene.render_dot_line(self.scene.curve)

            glfw.swap_buffers(self.window)
            glfw.poll_events()

        # clean up and exit
        glfw.terminate()


def main():
    print("Simple glfw render Window")
    rw = RenderWindow()
    rw.run()


if __name__ == '__main__':
    main()
