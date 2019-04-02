# Overview

The idea is that we pull data on an instance inside the VPC, store it in
CSV, push it over using restricted rsync, then load it into the local
postgres database on the bflabs instance.

Since we'll be dealing with daily data, we will always push over the last
month of daily data so that we have plenty of buffer should for some reason
the sync not happen every day.
