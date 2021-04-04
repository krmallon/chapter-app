import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SearchService } from '../services/search.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {

  constructor(public searchService: SearchService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    // this.searchService.searchBooks(this.route.snapshot.params.query)
    let url = this.route['_routerState'].snapshot.url;
    let query = this.route.snapshot.params.query

    if (url == '/search/books/' + query) {
      this.searchService.searchBooks(query)
    } 
    else if (url == '/search/users/' + query) {
      this.searchService.searchUsers(query)
    }
  }

}
