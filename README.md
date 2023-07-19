# Cubic-Bezier-Spline-Tool

This project involves building a limited pen tool that creates and manipulates a cubic Bezier spline. The program allows users to add nodes by clicking on the window, connect these nodes as a spline, and render the spline. Users can move existing nodes and their control points to modify the spline.

## Instructions

1. Clone this repository or download the necessary files.
2. Make sure you have the required libraries installed (OpenGL, GLFW).
3. Run the provided Python script to use the cubic Bezier spline drawing tool.

## How to Run

1. Install the required libraries using the following command (if you haven't already):

```bash
pip install glfw PyOpenGL
```

2. Run the script with command line arguments:

```bash
python cubic_bezier_spline.py screen_width screen_height
```

Replace `screen_width` and `screen_height` with the desired dimensions of the window.

## Setup

1. The projection matrix and viewport are set to match the window coordinates.
2. Multisampling is enabled four times for anti-aliasing.

## Rendering

Assuming you have a list of nodes and control points, the program performs the following rendering steps:

1. The spline is rendered as a set of independent cubic Bezier curves, with each curve represented as a polyline with 200 line segments. The line width can be increased for a smoother appearance.
2. Nodes are rendered as square points with a specified size using `GL_POINTS`.
3. Control points are rendered as round points using `GL_POINTS` and are smoothed for a better appearance.
4. Dotted lines connect control points to their associated nodes using `GL_LINES` with a stipple pattern.

## Interaction

Users can interact with the program using mouse and keyboard controls:

1. Left-clicking and holding on an existing node allows the node to be repositioned under the cursor as long as the left mouse button is held. The node's associated control points move along with it, maintaining the same offset.
2. Left-clicking and holding on an existing control point allows it to be repositioned under the cursor. If the node is an interior node, its second control point is also moved, ensuring that both control points and the node remain co-linear.
3. Left-clicking in the window (not on an existing node) adds a new node to the spline. The new node is created at the cursor's position with one control point placed 50 pixels above the node. The closer end point of the spline becomes an intermediate node, and the new node becomes the new end point. A second control point is added to the intermediate node, following the rules mentioned earlier.
4. Pressing the "E" key on the keyboard deletes all nodes and control points, resetting the program to its initial state.
