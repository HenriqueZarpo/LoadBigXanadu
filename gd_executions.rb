require 'rubygems' if RUBY_VERSION < '1.9'
require 'rest_client'
require 'json'

def read_line_number(filename, number)
  return nil if number < 1
  line = File.readlines(filename)[number-1]
  line ? line.chomp : nil
end

username = read_line_number('auth.txt',1)
pass = read_line_number('auth.txt',2)

require_relative 'C:\\GoodDataAgent\\zarpo_files_operations'
$log = File.open("C:\\GoodDataAgent\\log_ruby.txt", 'a+')
$serverapi = 'https://analytics.totvs.com.br/gdc/'
values = '{
  "postUserLogin": {
    "login": "user",
    "password": "authpass",
    "remember": 1
  }
}'
values.sub! 'user', username
values.sub! 'authpass', pass
headers = {
  :content_type => 'application/json',
  :accept => 'application/json',
}


status = ""
while (status != "OK") do	
	response = RestClient.post ($serverapi+'account/login'), values, headers
	cookies = response.cookies
	headers[:cookies] = cookies
	response = RestClient.get ($serverapi+'account/token'), headers
	cookies = response.cookies

	resource = RestClient::Resource.new($serverapi+'projects/xe3y4bx5vbqbbrcjjkcegmn889r1fjyx/dataload/processes/d92a960d-684b-4239-87e9-4b38e17cb081/executions?offset=0&limit=1', :headers => headers, :cookies=>cookies)
	response = resource.get()
	#~ puts response
	js = JSON.parse(response)
	print js
	if js["executions"]["items"].length>0
		status = js["executions"]["items"][0]["executionDetail"]["status"]
	else
		status="NO THREAD"
	end
	$log.write(status+"\n")
	if status == "ERROR" 
		open('emailtxt.txt', 'w') do |f|
			f.puts "\n ETL process in GD did not work!"
		end
		abort("error in the execution of the process, aborting...")
	elsif status=="NO THREAD"
		print "no running thread, we go on"
	    status="OK" 
	elsif status != "OK" 
		$log.write("execution not finished yet, sleeping for 5 more minutes\n")
		print("execution not finished yet, sleeping for 5 more minutes\n")
		sleep 300
	end
end
print "execution of the graph succesful... transfering files from GD to Responsys\n"
open('emailtxt.txt', 'w') do |f|
  f.puts "ETL process in GD Worked!"
end
#$log.write( "execution of the graph succesful... transfering files from GD to Responsys\n")
#fromGDtoResponsys()


