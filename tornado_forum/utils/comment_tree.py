from typing import List, Dict

def build_comment_tree(comments:List)->List:
    comment_map = {comment.id: comment for comment in comments}
    root_comments = []

    for comment in comments:
        parent_id = comment.parent_id
        comment.depth = get_depth_of_a_comment(comment, comment_map)
        if parent_id is None:
            root_comments.append(comment)
        else:
            parent_comment = comment_map.get(parent_id)
            if parent_comment:
                if not hasattr(parent_comment, 'children_in_tree'):
                    parent_comment.children_in_tree = []
                parent_comment.children_in_tree.append(comment)
    return root_comments

def get_depth_of_a_comment(comment, comment_map:Dict)->int:
    depth = 1
    while comment.parent_id is not None:
        depth = depth + 1
        comment = comment_map.get(comment.parent_id)
    return depth