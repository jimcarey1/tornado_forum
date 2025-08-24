def build_comment_tree(comments):
    """
    Builds a hierarchical comment tree from a flat list of comments.
    
    Args:
        comments (list): A list of Comment objects.
        
    Returns:
        list: A list of root comments, each with their children populated.
    """
    comment_map = {comment.id: comment for comment in comments}
    root_comments = []

    for comment in comments:
        parent_id = comment.parent_id
        if parent_id is None:
            # It's a root-level comment
            root_comments.append(comment)
        else:
            # It's a child comment, so link it to its parent
            parent_comment = comment_map.get(parent_id)
            if parent_comment:
                # Add the child to the parent's children list
                if not hasattr(parent_comment, 'children_in_tree'):
                    parent_comment.children_in_tree = []
                parent_comment.children_in_tree.append(comment)
    
    return root_comments