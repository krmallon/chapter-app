import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommentService } from '../services/comment.service';
import { GroupService } from '../services/group.service';

@Component({
  selector: 'app-group',
  templateUrl: './group.component.html',
  styleUrls: ['./group.component.scss']
})
export class GroupComponent implements OnInit {

  POST_OBJECT_TYPE = 6;

  constructor(public groupService: GroupService, public commentService: CommentService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.groupService.getGroup(this.route.snapshot.params.id)
    this.groupService.getMembers(this.route.snapshot.params.id)
    this.groupService.getPosts(this.route.snapshot.params.id)
  }

  getPostComments(post_id) {
    this.commentService.getComments(this.POST_OBJECT_TYPE, post_id)
  }

}
