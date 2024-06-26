�blip_coords �                   �
    � C�      C�     C�     M ����  M ���� � ����                    ����FLAG   SRC �  {$CLEO .cs}

// This script gets the coordinates of the red marker and prints them on the screen

script_name "blip_coords"
wait 1000


:GetBlipCoords
// Define variables to store the coordinates
0@ = 0.0  // X coordinate
1@ = 0.0  // Y coordinate
2@ = 0.0  // Z coordinate

// Loop to constantly check for the red marker
while true
    // Use 0AB6 to get the target blip (red marker) coordinates
    0AB6: store_target_marker_coords_to 0@ 1@ 2@ // IF and SET

    // Check if the red marker exists by verifying non-zero coordinates
    if and
        0@ <> 0.0
        1@ <> 0.0
        2@ <> 0.0
    then
        // If the marker exists, print the coordinates to the screen
        //0AD1: show_formatted_text_highpriority "X: %0.5f, Y: %0f, Z: %0.5f" time 500 0@ 2@ 1@
        0000: NOP
    else_jump @SetBlipZero  
    end
    
    wait 500
end

:SetBlipZero
0@ = 0.0
1@ = 0.0
2@ = 0.0
jump @GetBlipCoords�   __SBFTR 