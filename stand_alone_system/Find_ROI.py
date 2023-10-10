import cv2

# Function to draw a bounding box on a frame
def draw_bounding_box(frame):
    # Define the coordinates for the bounding box
    top_left = (0, 0)
    bottom_right = (600, 600)

    # Draw the bounding box on the frame
    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

# Open a video capture object (0 for the default camera)
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    if not ret:
        break

    # Draw the bounding box on the frame
    draw_bounding_box(frame)

    # Display the frame with the bounding box
    cv2.imshow('Frame with Bounding Box', frame)

    # Break the loop when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()
