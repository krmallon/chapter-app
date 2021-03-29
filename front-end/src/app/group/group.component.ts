import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GroupService } from '../services/group.service';

@Component({
  selector: 'app-group',
  templateUrl: './group.component.html',
  styleUrls: ['./group.component.scss']
})
export class GroupComponent implements OnInit {

  constructor(public groupService: GroupService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.groupService.getGroup(this.route.snapshot.params.id)
    this.groupService.getMembers(this.route.snapshot.params.id)
    this.groupService.getPosts(this.route.snapshot.params.id)
  }

}
