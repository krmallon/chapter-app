import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SearchService } from '../services/search.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {

  constructor(private searchService: SearchService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.searchService.searchBooks(this.route.snapshot.params.query)
  }

}
