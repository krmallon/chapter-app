import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SearchService } from '../services/search.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {

  page = 0;
  startIndex = 0;
  lang = 'en';
  order = 'relevance'
  type;

  constructor(public searchService: SearchService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    // this.searchService.searchBooks(this.route.snapshot.params.query)
    let url = this.route['_routerState'].snapshot.url;
    let query = this.route.snapshot.params.query

    if (url.includes('/search/books/')) {
      this.type = 'books'
      this.searchService.searchBooks(query, this.startIndex, this.lang, this.order)
    } 
    else if (url.includes('/search/users/')) {
      this.type = 'users'
      this.searchService.searchUsers(query)
    }
  }

  nextPage() {
    this.startIndex = this.startIndex + 30;
    this.searchService.searchBooks(this.route.snapshot.params.query, this.startIndex, this.lang, this.order)
  }

  previousPage() {
    this.startIndex = this.startIndex - 30;
    this.searchService.searchBooks(this.route.snapshot.params.query, this.startIndex, this.lang, this.order)
  }

  setLang(language) {
    this.lang = language;
    this.searchService.searchBooks(this.route.snapshot.params.query, this.startIndex, this.lang, this.order)
  }

  setOrder(order) {
    this.order = order;
    this.searchService.searchBooks(this.route.snapshot.params.query, this.startIndex, this.lang, this.order)
  }
}
