import maya.cmds as cmds

def get_selected_side_prefix():
    sel = cmds.ls(selection=True, type="joint")
    if not sel or len(sel) != 1:
        cmds.error("Please select the top joint of the leg chain (e.g., L_leg or R_leg).")
    top_joint = sel[0]
    if not ("L_" in top_joint or "R_" in top_joint):
        cmds.error("Selected joint must start with 'L_' or 'R_'.")
    return top_joint[:2]  # 'L_' or 'R_'



def create_reverse_foot_locators():
    locators = ["Heel_Loc", "Ball_Loc", "Toe_Loc"]
    created = []

    for loc in locators:
        if not cmds.objExists(loc):
            cmds.spaceLocator(name=loc)
            cmds.setAttr(f"{loc}.overrideEnabled", 1)
            cmds.setAttr(f"{loc}.overrideColor", 17)
            created.append(loc)
            
    # Freeze transforms on locators
    for loc in created:
        cmds.makeIdentity(loc, apply=True, t=True, r=True, s=True, n=0)


    if created:
        cmds.select(created)
        print("Locators created. Please position them at the heel, ball, and toe pivots before building the rig.")
    else:
        print("All locators already exist. You can reposition them or proceed to build the rig.")


def auto_place_reverse_foot_locators():
    side = get_selected_side_prefix()
    joint_map = {
        "Heel_Loc": f"{side}toe",
        "Ball_Loc": f"{side}toe",
        "Toe_Loc": f"{side}toe_end"
    }

    created = []
    for loc, joint in joint_map.items():
        if not cmds.objExists(joint):
            cmds.error(f"Joint {joint} not found. Please check your hierarchy.")
        if not cmds.objExists(loc):
            pos = cmds.xform(joint, q=True, ws=True, t=True)
            cmds.spaceLocator(name=loc, p=pos)
            cmds.setAttr(f"{loc}.overrideEnabled", 1)
            cmds.setAttr(f"{loc}.overrideColor", 18)
            created.append(loc)
            print(f"Placed {loc} at {joint}")
        else:
            print(f"{loc} already exists. Skipping.")
            
    # Freeze transforms on newly created locators
    for loc in created:
        cmds.makeIdentity(loc, apply=True, t=True, r=True, s=True, n=0)


    if created:
        cmds.select(created)
        print("Auto-placed locators. You can adjust them before building the rig.")


def build_reverse_foot_rig():
    
    side = get_selected_side_prefix()

    leg_joint = f"{side}leg"
    foot_joint = f"{side}foot"
    toe_joint = f"{side}toe"
    toe_end_joint = f"{side}toe_end"
    foot_ctl = f"{side}foot_CTL"
    
    # Create IK handles
    cmds.ikHandle(startJoint=leg_joint, endEffector=foot_joint, name="legIK")
    cmds.ikHandle(startJoint=foot_joint, endEffector=toe_joint, solver="ikSCsolver", name="BallIK")
    cmds.ikHandle(startJoint=toe_joint, endEffector=toe_end_joint, solver="ikSCsolver", name="ToeIK")
    
    # Use existing locators
    if not all(cmds.objExists(loc) for loc in ["Heel_Loc", "Ball_Loc", "Toe_Loc"]):
        cmds.error("Please create and position Heel_Loc, Ball_Loc, and Toe_Loc before building the rig.")
    
    toe_loc = "Toe_Loc"
    ball_loc = "Ball_Loc"
    heel_loc = "Heel_Loc"
    
    # Parent IK handles under locators
    cmds.parent("legIK", heel_loc)
    cmds.parent("BallIK", ball_loc)
    cmds.parent("ToeIK", ball_loc)

    
    # Parent locators
    cmds.parent(heel_loc, toe_loc)
    cmds.parent(ball_loc, toe_loc)
    cmds.parent(toe_loc, foot_ctl)
    
    # Add attributes to foot controller
    attrs = ["PeelHeel", "ToeTap", "ToeTwist", "ToeTip"]
    for attr in attrs:
        cmds.addAttr(foot_ctl, longName=attr, attributeType="double", defaultValue=0, keyable=True)
    
    # Connect attributes to locators
    cmds.connectAttr(f"{foot_ctl}.PeelHeel", "Heel_Loc.rotateX", force=True)
    cmds.connectAttr(f"{foot_ctl}.ToeTap", "Ball_Loc.rotateX", force=True)
    cmds.connectAttr(f"{foot_ctl}.ToeTwist", "Toe_Loc.rotateY", force=True)
    cmds.connectAttr(f"{foot_ctl}.ToeTip", "Toe_Loc.rotateX", force=True)


def build_reverse_foot_ui():
    if cmds.window("reverseFootWin", exists=True):
        cmds.deleteUI("reverseFootWin")

    cmds.window("reverseFootWin", title="Reverse Foot Rig Tool", widthHeight=(260, 160))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Place Heel, Ball, and Toe locators", font="boldLabelFont")
    cmds.separator(height=10, style="in")

    cmds.button(label="Create Locators- Manual Placement", height=30, command=lambda x: create_reverse_foot_locators())
    cmds.button(label="Build Reverse Foot Rig", height=40, command=lambda x: build_reverse_foot_rig())
    cmds.button(label="Auto Place Locators", height=40, command=lambda x: auto_place_reverse_foot_locators())

    cmds.showWindow("reverseFootWin")

build_reverse_foot_ui()