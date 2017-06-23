#!/usr/bin/ruby
# -*- coding: utf-8 -*-
require 'pragmatic_segmenter'
FILE_DIR = "/raid/ltj/YEEYAN_/merged_mixture"
SAVE_DIR = "/raid/ltj/YEEYAN_/3_result_mixture_diff_0"

puts 'segmenter starting'
i = 0
file_list = Dir::entries(FILE_DIR)
file_list.each do |file_name|
    if file_name == '.' or file_name == '..'
        next
    end
    file_path = FILE_DIR + '/' + file_name
    save_path = SAVE_DIR + '/' + file_name
    if File.exist?(save_path)
    	next
    end
    puts file_name
    lines = IO.readlines(file_path)
    lines.each do |text|
        ps = PragmaticSegmenter::Segmenter.new(text:text)    
        if ps.segment.length < 1
            next
        end
        f = File.open(save_path,'a+')
        f.puts ps.segment
        f.puts ps.segment.length
        f.puts
        f.close
    end
    i += 1
    if i%100 == 0
        puts i.to_s + ' file has been segment'
    end

end

puts "DOWN"