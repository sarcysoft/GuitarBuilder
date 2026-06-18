// Function to create a cylinder extruded from point1 to point2 on the horizontal plane
// The cylinder is vertical at point1 and dragged to point2, filling the space between
// Parameters:
//   point1: [x, y] - Starting point on the horizontal plane
//   point2: [x, y] - Ending point on the horizontal plane
//   radius: Radius of the cylinder
//   height: Vertical height of the cylinder

module cylinder_between_points(point1, point2, radius=1, height=10) {
    // Use hull to fill the space between two vertical cylinders
    hull() {
        // Cylinder at point1
        translate([point1[0], point1[1], 0])
            cylinder(r=radius, h=height, center=false, $fn=50);
        
        // Cylinder at point2
        translate([point2[0], point2[1], 0])
            cylinder(r=radius, h=height, center=false, $fn=50);
    }
}

// Example usage:
// Create a cylinder from point [0, 0] to point [10, 5]
// cylinder_between_points([0, 0], [10, 5], radius=0.5, height=20);

// Function to create cylinders along a sequence of points
// Parameters:
//   points: Array of [x, y] coordinates
//   radius: Radius of the cylinders
//   height: Vertical height of the cylinders
//   fill_polygon: If true, also creates an extruded polygon through all points

module cylinder_path(points, radius=1, height=10, fill_polygon=false) {
    union() {
        // Loop through each consecutive pair of points
        for (i = [0 : len(points) - 2]) {
            cylinder_between_points(points[i], points[i+1], radius, height);
        }
        
        // If fill_polygon is true, close the path and create an extruded polygon
        if (fill_polygon) {
            // Close the path by connecting last point to first point
            cylinder_between_points(points[len(points)-1], points[0], radius, height);
            
            // Create the filled polygon
            linear_extrude(height=height)
                polygon(points);
        }
    }
}

// Example usage of cylinder_path:
// Create a path through multiple points
// cylinder_path([[0, 0], [10, 5], [15, 15], [5, 20]], radius=0.5, height=10, fill_polygon=true);

// Additional examples (commented out):
// cylinder_between_points([5, 5], [15, 10], radius=1, height=15);
// cylinder_between_points([-5, -5], [5, 5], radius=0.75, height=25);
