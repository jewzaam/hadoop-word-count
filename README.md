# GOALS
1) make wake county realestate data available in hdfs
2) batch process (MR) the data in some dummy way (word count?)
3) extract meaningful data (MR)
4) make it real time

# QUESTIONS
- How do changes to a file get into HDFS?
- For files that change over time, how does the delta get processed without reprocessing the full source?

# Things I've Done

## setup single cluster hadoop
http://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html
http://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html#Standalone_Operation

## create project
mvn -B archetype:generate -DarchetypeGroupId=org.apache.maven.archetypes -DgroupId=org.jewzaam -DartifactId=hadoop-word-count
cd hadoop-word-count
rm -f `find -name *.java`
git init
git add .
git commit -am "Initial commit"

## create src/main/java/org/jewzaam/WordCount.java
From http://hortonworks.com/hadoop-tutorial/introducing-apache-hadoop-developers/

## add dependencies
```xml
        <dependency>vi 
            <groupId>org.apache.hadoop</groupId>
            <artifactId>hadoop-mapreduce-client-core</artifactId>
            <version>2.6.0</version>
        </dependency>
        <dependency>
            <groupId>org.apache.hadoop</groupId>
            <artifactId>hadoop-core</artifactId>
            <version>1.2.1</version>
        </dependency>
```

## build, scrape, MR
mvn clean install
./scrape-wake-gov-realestate.py 0 100 --output target/input/usa/nc/wake/realestate/home --threads 100 --logdir target
hadoop jar ./target/hadoop-word-count-1.0-SNAPSHOT.jar org.jewzaam.WordCount ./target/input/usa/nc/wake/realestate/home/ ./target/output/usa/nc/wake/realestate/home/count
