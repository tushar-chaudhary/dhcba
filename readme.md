deployed on heroku.

Url = https://dhcapi.herokuapp.com/


case Status
https://dhcapi.herokuapp.com/<cnum>/<ctype>/<cyear>
http://dhcapi.herokuapp.com/9242/W.P.(C)/2014


judges Roster
https://dhcapi.herokuapp.com/judges_roster


cause List
https://dhcapi.herokuapp.com/cause_list


nominated Counsel
https://dhcapi.herokuapp.com/nominated_counsel


Delhi High Court history
https://dhcapi.herokuapp.com/history


sitting judges
https://dhcapi.herokuapp.com/sjudges


Real time download forms
https://dhcapi.herokuapp.com/Updateddforms


Quick Access of download forms
https://dhcapi.herokuapp.com/qforms




Dictionary
https://dhcapi.herokuapp.com/dictionary/


certified_copy by applied by
https://dhcapi.herokuapp.com/ccappliedby/<applied_by>/<diary_yr>/<cyear>
https://dhcapi.herokuapp.com/ccappliedby/gautam/2017/2014


certified_copy
https://dhcapi.herokuapp.com/ccopies/<caseno>/<cyear>/<diary_yr>
https://dhcapi.herokuapp.com/ccopies/9242/2014/2017

calender
https://dhcapi.herokuapp.com/calender

general notices
https://dhcapi.herokuapp.com/notices

act
https://dhcapi.herokuapp.com/act/

dictionary
https://dhcapi.herokuapp.com/d/<word>

Ex: https://dhcapi.herokuapp.com/d/abstract

ebooks
https://dhcapi.herokuapp.com/book/<book>
Ex: https://dhcapi.herokuapp.com/book/LAW OF ATTORNEY AND CLIENT (1896)

##Flask Migrations
Running migrations -
    flask db init
    flask db migrate
    flask db upgrade

This will make the models update the server's schema
