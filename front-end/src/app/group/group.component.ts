import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
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
  newPostForm;

  constructor(public groupService: GroupService, public commentService: CommentService, private route: ActivatedRoute, private formBuilder: FormBuilder) { }

  ngOnInit(): void {

    this.newPostForm = this.formBuilder.group({
      title: ['', Validators.required],
      text: ['', Validators.required]
    })

    this.groupService.getGroup(this.route.snapshot.params.id)
    this.groupService.getMembers(this.route.snapshot.params.id)
    this.groupService.getPosts(this.route.snapshot.params.id)
  }

  getPostComments(post_id) {
    this.commentService.getComments(this.POST_OBJECT_TYPE, post_id)
  }

}
