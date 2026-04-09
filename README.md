# Y Combinator companies API

This repository contains an unofficial API for Y Combinator companies fetched from the Y Combinator website's.

<!--start generated readme-->
<!--end generated readme-->

## 📀 Schema

Each endpoint (with the exception of `meta.json`) returns an array of objects.
Each object has the following properties:

| Property                | Type     | Description                                                      |
| ----------------------- | -------- | ---------------------------------------------------------------- |
| `id`                    | number   | The company's ID decided by Y Combinator                         |
| `name`                  | string   | The company's name                                               |
| `slug`                  | string   | The company's human-readable slug                                |
| `former_names`          | string[] | The company's former names, if the company was renamed           |
| `small_logo_thumb_url`  | string   | The URL of the company's logo as a square hosted by Y Combinator |
| `website`               | string   | The company's website URL                                        |
| `all_locations`         | string   | The company's locations separated by colons (;)                  |
| `long_description`      | string   | The company's long description                                   |
| `one_liner`             | string   | The company's one-liner description                              |
| `team_size`             | number   | The company's team size                                          |
| `highlight_black`       | boolean  | Whether the company is highlighted for Black founders            |
| `highlight_latinx`      | boolean  | Whether the company is highlighted for Hispanic/Latino founders  |
| `highlight_women`       | boolean  | Whether the company is highlighted for women founders            |
| `industry`              | string   | The company's industry                                           |
| `subindustry`           | string   | The company's subindustry                                        |
| `launched_at`           | number   | The company's launch date as a Unix timestamp                    |
| `tags`                  | string[] | The company's tags                                               |
| `top_company`           | boolean  | Whether the company is a top company                             |
| `isHiring`              | boolean  | Whether the company is hiring                                    |
| `nonprofit`             | boolean  | Whether the company is a nonprofit                               |
| `batch`                 | string   | The company's batch                                              |
| `status`                | string   | The company's status                                             |
| `industries`            | string[] | The company's industries                                         |
| `regions`               | string[] | The company's regions                                            |
| `stage`                 | string   | The company's stage                                              |
| `app_video_public`      | boolean  | Whether the company's app video is public                        |
| `demo_day_video_public` | boolean  | Whether the company's demo day video is public                   |
| `app_answers`           | object   | The company's app answers                                        |
| `question_answers`      | boolean  | Whether the company's question answers are public                |
| `url`                   | string   | The company's URL on the Y Combinator website                    |
| `api`                   | string   | The company's API endpoint from this repository                  |

For example, the `airbnb.json` endpoint returns the following object:

```json
{
  "id": 271,
  "name": "Airbnb",
  "slug": "airbnb",
  "former_names": [],
  "small_logo_thumb_url": "https://bookface-images.s3.amazonaws.com/small_logos/3e9a0092bee2ccf926e650e59c06503ec6b9ee65.png",
  "website": "http://airbnb.com",
  "all_locations": "San Francisco, CA, USA",
  "long_description": "Founded in August of 2008 and based in San Francisco, California, Airbnb is a trusted community marketplace for people to list, discover, and book unique accommodations around the world — online or from a mobile phone. Whether an apartment for a night, a castle for a week, or a villa for a month, Airbnb connects people to unique travel experiences, at any price point, in more than 33,000 cities and 192 countries. And with world-class customer service and a growing community of users, Airbnb is the easiest way for people to monetize their extra space and showcase it to an audience of millions.  \r\n\r\nNo global movement springs from individuals. It takes an entire team united behind something big. Together, we work hard, we laugh a lot, we brainstorm nonstop, we use hundreds of Post-Its a week, and we give the best high-fives in town. Headquartered in San Francisco, we have satellite offices in Dublin, London, Barcelona, Paris, Milan, Copenhagen, Berlin, Moscow, São Paolo, Sydney, and Singapore.",
  "one_liner": "Book accommodations around the world.",
  "team_size": 6132,
  "highlight_black": false,
  "highlight_latinx": false,
  "highlight_women": false,
  "industry": "Consumer",
  "subindustry": "Consumer -> Travel, Leisure and Tourism",
  "launched_at": 1326790856,
  "tags": ["Marketplace", "Travel"],
  "tags_highlighted": [],
  "top_company": true,
  "isHiring": false,
  "nonprofit": false,
  "batch": "W09",
  "status": "Public",
  "industries": ["Consumer", "Travel, Leisure and Tourism"],
  "regions": ["United States of America", "America / Canada"],
  "stage": "Growth",
  "app_video_public": false,
  "demo_day_video_public": false,
  "app_answers": null,
  "question_answers": false,
  "url": "https://www.ycombinator.com/companies/airbnb",
  "api": "https://devasheeshg.github.io/yc-api/batches/w09/airbnb.json"
}
```
