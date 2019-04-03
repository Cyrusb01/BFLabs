# Overview

The idea is that we pull data on an instance inside the VPC, store it in
CSV, push it over using restricted rsync, then load it into the local
postgres database on the bflabs instance.

Since we'll be dealing with daily data, we will always push over all daily
data from the beginning of time.

 1. Prepare the data shortly after midnight UTC. This results in a bunch of csv files.
 2. rsync the data over to the bflabs server.
 3. Read them into the local postgres database. Done.
 
